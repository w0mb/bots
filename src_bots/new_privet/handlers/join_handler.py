import asyncio

from aiogram import Bot
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ChatJoinRequest, CallbackQuery, Message
from aiogram.filters import Command


from src_bots.new_privet.handlers.helpers.join_funcs import (
    update_channel_file, is_user_member, pic_spam, spam, approve
)

from src_bots.new_privet.handlers.base_handler import BaseHandler
from src_bots.new_privet.keybords.keyboard_manager import KeyboardManager

class JoinHandler(BaseHandler):
    def __init__(self, keyboard_manager: KeyboardManager | None):
        super().__init__()
        self.join_request_data = {}
        self.keyboard_manager = keyboard_manager
        self.sleep_time = 3600
        self.spam_type = "both"
        self.wait_for_approve = 1000
        self.send_count1 = 5
        self.send_count2 = 5

        class Form(StatesGroup):
            add_sleep = State()
            add_spam_type = State()
            add_wait_for_approve = State()

        @self.router.message(Command(commands=["addsleep"]))
        async def add_sleep_handler(msg: Message, bot: Bot, state: FSMContext):
            await msg.answer("введите количество милисекунд задержки перед отправкой спам-сообщения(3600мс = 1час)\n"
                             "по умолчанию задержка = 1 часу\n"
                             "!это команда перезаписывает значение задержки!\n"
                             "т.е. если у вас была установлена задержка 100000мс и вы вызываете команду снова, передавая в нее значение 1мс\n"
                             "тогда задержка будет равна новому значению 1мс")

            @self.router.message(Form.add_sleep)
            async def add_sleep():
                self.sleep_time = int(msg.text)
                await state.clear()

        @self.router.message(Command(commands=["spamtype"]))
        async def spam_type_handler(msg: Message, bot: Bot, state: FSMContext):
            await msg.answer("выбери тип спама\n"
                             "both - оба варианта(картинка с кнопками и текст с ссылкой)\n"
                             "only_text - только текст с ссылкой\n"
                             "only_pic - картинка с кнопками, в которых ссылки\n"
                             "выбор типа также перезаписывает предыдущее состояние, по умолчанию стоит вариант both\n"
                             "сообщения будут отправлять по 5 раз")
            @self.router.message(Form.add_spam_type)
            async def spam_type():
                self.spam_type = msg.text
                await state.clear()

        @self.router.message(Command(commands=["approvesleep"]))
        async def spam_type_handler(msg: Message, bot: Bot, state: FSMContext):
            await msg.answer("напиши сколько боту ждать в милисекундах прежде чем впустить пользователя в канал,\n"
                             "когда пользователь нажимает 'Подтвердить' на клавитуре\n"
                             "1 час = 3600мс, по умолчанию стоит 1000мс\n"
                             "ввод данных перезаписывает предыдущее значение")
            @self.router.message(Form.add_wait_for_approve)
            async def spam_type():
                self.wait_for_approve = int(msg.text)
                await state.clear()

        @self.router.my_chat_member()#вынести в отдельный хендлер
        async def handle_bot_added(update: types.ChatMemberUpdated, bot: Bot):
            chat = update.chat
            new_status = update.new_chat_member.status
            await update_channel_file(str(chat.id), chat.title, new_status, bot)

        @self.router.chat_join_request()
        async def handle_join_request(join_request: ChatJoinRequest, bot: Bot):
            send_count1 = 5
            send_count2 = 5
            user_id = join_request.from_user.id
            channel_id = join_request.chat.id
            bot_info = await bot.get_me()
            bot_id = bot_info.id

            self.join_request_data[user_id] = channel_id#сделать дикий рефактор этой темы
            async def send_pic_spam():
                for i in range(1, self.send_count1 + 1):
                    if not await is_user_member(bot, user_id, channel_id):
                        await pic_spam(bot, user_id, str(i), keyboard_manager.get_keyboard(bot_id).get_keyboard())
                    await asyncio.sleep(self.sleep_time)

            async def send_text_spam():
                for i in range(1, self.send_count2 + 1):
                    if not await is_user_member(bot, user_id, channel_id):
                        await spam(bot, user_id)
                    await asyncio.sleep(self.sleep_time)

            if self.spam_type == "both":
                await send_pic_spam()
                await send_text_spam()
            elif self.spam_type == "only_text":
                await send_text_spam()
            elif self.spam_type == "only_pic":
                await send_pic_spam()

        @self.router.callback_query(lambda c: c.data.startswith("confirm"))#вынести тоже в отдельный хендлер
        async def handle_confirm_request(callback: CallbackQuery):
            bot = callback.bot
            user_id = callback.from_user.id
            channel_id = self.join_request_data.get(user_id)

            if channel_id:
                await callback.answer("Ваша заявка скоро будет одобрена!")
                await asyncio.sleep(self.wait_for_approve)
                await approve(bot, user_id, channel_id)
                await callback.answer("Ваша заявка одобрена!")
                self.join_request_data.pop(user_id, None)
            else:
                await callback.answer("Ошибка: данные не найдены.")