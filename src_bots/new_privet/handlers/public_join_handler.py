import os
import re

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.filters import ChatMemberUpdatedFilter, KICKED, LEFT, MEMBER, ADMINISTRATOR, CREATOR, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ChatMemberUpdated, Message, FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup

from src_bots.new_privet.handlers.base_handler import BaseHandler
from src_bots.new_privet.handlers.helpers.join_funcs import is_user_member
from src_bots.new_privet.keybords.keyboard_manager import KeyboardManager
from src_bots.new_privet.utils.file_utils import get_strings_from_file


class PublicJoinHandler(BaseHandler):
    def __init__(self, keyboard_manager: KeyboardManager | None):
        super().__init__()
        self.welcome_text = ""
        self.video_path = None
        self.button_text = "Перейти"
        self.url = None

        os.makedirs("videos", exist_ok=True)

        class Form(StatesGroup):
            set_welcome_video = State()
            set_welcome_text = State()
            set_button_text = State()

        @self.router.message(Command(commands=["setwelcomebuttontextpublic"]))
        async def set_button_text_handler(msg: Message, state: FSMContext):
            await msg.answer("Введите текст, который будет написан на кнопке(Дефолт='Перейти')")
            await state.set_state(Form.set_button_text)
            @self.router.message(Form.set_button_text)
            async def set_button_text(msg: Message, state: FSMContext):
                self.button_text = msg.text
                await state.clear()

        @self.router.message(Command(commands=["setwelcomepublic"]))
        async def set_welcome_text_handler(msg: Message, state: FSMContext):
            await msg.answer("Введите текст, который будет отправлен пользователю, когда тот попдишется на публичный канал")
            await state.set_state(Form.set_welcome_text)
            @self.router.message(Form.set_welcome_text)
            async def set_welcome_text(msg: Message, state: FSMContext):
                self.welcome_text = msg.html_text

                url_pattern = r'href=["\'](https?://[^"\']+)["\']'
                urls = re.findall(url_pattern, msg.html_text)

                if urls:
                    self.url = urls[0]
                else:
                    self.url = None

                await msg.answer(f"текст, который был установлен:\n"
                            f"{self.welcome_text}", parse_mode=ParseMode.HTML)

                await state.clear()
        @self.router.message(Command(commands=["setwelcomevideopublic"]))
        async def set_welcome_video_handler(msg: Message, state: FSMContext):
            await msg.answer("Отправьте видео, которое будет использовано в приветственном сообщении.")
            await state.set_state(Form.set_welcome_video)
            @self.router.message(Form.set_welcome_video)
            async def save_welcome_video(msg: Message, state: FSMContext):
                if not msg.video:
                    await msg.answer("Ошибка: пожалуйста, отправьте именно видео.")
                    return

                bot_info = await msg.bot.get_me()
                bot_id = bot_info.id
                video_filename = f"videos/welcome_{bot_id}.mp4"

                # Удаляем старое видео, если есть
                if self.video_path and os.path.exists(self.video_path):
                    os.remove(self.video_path)

                # Сохраняем новое видео
                self.video_path = video_filename
                await msg.bot.download(msg.video.file_id, self.video_path)

                await msg.answer("Видео успешно сохранено. Теперь оно будет отправляться новым подписчикам.")
                await state.clear()

        @self.router.chat_member()
        async def new_chat_member_handler(event: ChatMemberUpdated, bot: Bot):

            status = event.new_chat_member.status
            if status not in ['member', 'creator', 'administrator']:
                return

            bot_info = await bot.get_me()
            bot_id = bot_info.id
            self.video_path = f"videos/welcome_{bot_id}.mp4"
            print(self.url)
            kb = InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text=self.button_text, url=self.url)]]#ЭТО ХУЕТА ПРЯМ ЗДЕСЬ КЛАВУ СОЗДАВАТЬ,
                                                                                            # КОГДА ЕСТЬ КЛАСС КЛАВИАТУРЫ
            )
            channels = await get_strings_from_file(f"public_bot_channel_ids/{bot_id}.txt")

            for channel in channels:
                channel_id, channel_name, assigned_bot_id, _ = channel.split(":")
                if int(assigned_bot_id) == bot_id and int(channel_id) == event.chat.id:
                    if self.video_path and os.path.exists(self.video_path):
                        video = FSInputFile(self.video_path)
                        caption = self.welcome_text if self.welcome_text else None
                        if caption is None: return
                        await bot.send_video(event.from_user.id, video, caption=caption, parse_mode=ParseMode.HTML, reply_markup=kb)
                    elif self.welcome_text:
                        await bot.send_message(event.from_user.id, self.welcome_text, parse_mode=ParseMode.HTML, reply_markup=kb)

