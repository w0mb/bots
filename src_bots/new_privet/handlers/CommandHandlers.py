import os

from aiogram import Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup

from handlers.base_handler import BaseHandler
from utils.file_utils import save_string_to_file


class CommandHandlers(BaseHandler):
    def __init__(self, join_handler):
        super().__init__()
        self.join_handler = join_handler
        class Form(StatesGroup):
            add_sleep = State()
            add_spam_type = State()
            add_wait_for_approve = State()
            add_vid_cap = State()
            add_video_creo = State()
            add_url_to_buttons_cre = State()
            add_button_text_creo = State()
            add_vpusk = State()
            add_buttons_count = State()
            add_sand_count = State()

        @self.router.message(Command(commands=["getcaptioncreo"]))
        async def get_caption_to_video_handler(msg: Message):
            await msg.answer(f"Подпись к видео: {self.join_handler.video_caption}")
        @self.router.message(Command(commands=["setkbcreo"]))
        async def set_text_and_url_to_button_handler(msg: Message, state: FSMContext):
            await msg.answer("Пришли текст кнопки и ссылку для нее в формате текст$http://sadasd.com\n"
                             "если кнопок несколько, отравь текст и ссылку для каждой с новой строки в одном сообщении, например:\n\n\n"
                             "текст1$https://1.com\n\n"
                             "текст2$https://2.com\n\n"
                             "текст3$https://3.com\n\n"
                             "параметры только для спама типа creo")
            await state.set_state(Form.add_button_text_creo)
        @self.router.message(Form.add_button_text_creo)
        async def set_text_and_url_to_button(msg: Message, state: FSMContext, bot: Bot):
            self.join_handler.but_text = msg.html_text.strip()
            await msg.answer(f"Текст кнопки сохранен:\n"
                             f"{self.join_handler.but_text}")
            bot_info = await bot.get_me()
            bot_id = bot_info.id
            await save_string_to_file("but_text"+"#"+self.join_handler.but_text, f"settings/{bot_id}.txt")
            await state.clear()
        @self.router.message(Command(commands=["setcaptiontovideocreo"]))
        async def set_caption_to_video_handler(msg: Message, state: FSMContext):
            await msg.answer("Пришлите текст, который будет установлен как подпись к видео\n\n"
                             "параметры только для спама типа creo")
            await state.set_state(Form.add_vid_cap)
        @self.router.message(Form.add_vid_cap)
        async def vid_cap(msg: Message, state: FSMContext, bot: Bot):
            self.join_handler.video_caption = msg.html_text
            await msg.answer(f"Подпись к видео успешно сохранена!:\n\n"
                             f"{self.join_handler.video_caption}")
            bot_info = await bot.get_me()
            bot_id = bot_info.id
            await save_string_to_file("video_caption"+"#"+self.join_handler.video_caption, f"settings/{bot_id}.txt")
            await state.clear()
        @self.router.message(Command(commands=["setvpusk"]))
        async def set_vpusk(msg: Message, state: FSMContext):
            await msg.answer("отправьте либо 1 либо 0\n"
                             "1 - впускать\n"
                             "0 - не впускать\n"
                             "параметры только для спама типа creo")
            await state.set_state(Form.add_vpusk)
        @self.join_handler.router.message(Form.add_vpusk)
        async def vpusk(msg: Message, state: FSMContext, bot: Bot):
            self.join_handler.vpuskat = int(msg.text)
            await msg.answer(f"Впускать установлен на цифру от пользователя {self.join_handler.vpuskat}")
            bot_info = await bot.get_me()
            bot_id = bot_info.id
            await save_string_to_file("vpuskat"+"#"+str(self.join_handler.vpuskat), f"settings/{bot_id}.txt")
            await state.clear()

    # async def set_cre_buttons_count(self, msg: Message, state: FSMContext):
    #     await state.set_state(self.Form.add_buttons_count)
    #     await msg.answer("Отправь число, которое будет установлено как количество кнопок для крео(По умолчанию = 1)")
    #     @self.join_handler.router.message(self.Form.add_buttons_count)
    #     async def buttons_count(msg: Message):
    #         self.creo_but_count = int(msg.text)
    #         await msg.answer("Количество кнопок для крео установлено")
    #         await state.clear()
        @self.router.message(Command(commands=["setspamcount"]))
        async def set_send_spam_count(msg: Message, state: FSMContext):
            await msg.answer("Отправь число, которое будет установлено как количество спам сообщений(По умолчанию = 1)")
            await state.set_state(Form.add_sand_count)
        @self.join_handler.router.message(Form.add_sand_count)
        async def set_spam_count(msg: Message, state: FSMContext, bot: Bot):
            self.join_handler.send_count1 = int(msg.text)
            await msg.answer(f"Количество спам сообщений установлено на {self.join_handler.send_count1}")
            bot_info = await bot.get_me()
            bot_id = bot_info.id
            await save_string_to_file("send_count1"+"#"+str(self.join_handler.send_count1), f"settings/{bot_id}.txt")
            await state.clear()
        @self.router.message(Command(commands=["setvideocreo"]))
        async def set_video_creo_handler(msg: Message, bot: Bot, state: FSMContext):
            await msg.answer("пришлите видео, которое будет отправляться при спаме типа creo")
            await state.set_state(Form.add_video_creo)
        @self.join_handler.router.message(Form.add_video_creo)
        async def vid(msg: Message, bot: Bot, state: FSMContext):
            if msg.video:
                os.makedirs("videos/", exist_ok=True)
                video_file = await bot.get_file(msg.video.file_id)
                video_path = f"videos/{msg.video.file_id}.mp4"
                await bot.download_file(video_file.file_path, video_path)
                self.join_handler.video_path = video_path
                bot_info = await bot.get_me()
                bot_id = bot_info.id
                await save_string_to_file("video_path"+"#"+self.join_handler.video_path, f"settings/{bot_id}.txt")
                await msg.answer("Видео успешно сохранено!")
            else:
                await msg.answer("Пожалуйста, отправьте видео.")
            await state.clear()
        @self.router.message(Command(commands=["setsleep"]))
        async def add_sleep_handler(msg: Message, bot: Bot, state: FSMContext):
            await msg.answer("Введите количество секунд задержки перед отправкой спам-сообщения\n"
                             "По умолчанию задержка = 1 часу\n"
                             "!Эта команда перезаписывает значение задержки!\n"
                             "Т.е. если у вас была установлена задержка 100000сек и вы вызываете команду снова, передавая в нее значение 1сек\n"
                             "Тогда задержка будет равна новому значению 1сек")
            await state.set_state(Form.add_sleep)
        @self.join_handler.router.message(Form.add_sleep)
        async def add_sleep(msg: Message, state: FSMContext, bot: Bot):
            self.join_handler.sleep_time = int(msg.text)
            bot_info = await bot.get_me()
            bot_id = bot_info.id
            await save_string_to_file("sleep_time"+"#"+str(self.join_handler.sleep_time), f"settings/{bot_id}.txt")
            await state.clear()
        @self.router.message(Command(commands=["setspamtype"]))
        async def spam_type_handler(msg: Message, bot: Bot, state: FSMContext):
            await msg.answer("Выбери тип спама\n"
                             "both - оба варианта(картинка с кнопками и текст с ссылкой)\n"
                             "only_text - только текст с ссылкой\n"
                             "only_pic - картинка с кнопками, в которых ссылки\n"
                             "Выбор типа также перезаписывает предыдущее состояние, по умолчанию стоит вариант both\n"
                             "Сообщения будут отправлять по 1 разу\n"
                             "чтобы задать число сообщений отправьте /setspamcount")
            await state.set_state(Form.add_spam_type)
        @self.join_handler.router.message(Form.add_spam_type)
        async def spam_type(msg: Message, state: FSMContext, bot: Bot):
            self.join_handler.spam_type = msg.text
            await msg.answer(f"Вы установили: {self.join_handler.spam_type}")
            bot_info = await bot.get_me()
            bot_id = bot_info.id
            await save_string_to_file("spam_type"+"#"+self.join_handler.spam_type, f"settings/{bot_id}.txt")
            await state.clear()
        @self.router.message(Command(commands=["setapprovetime"]))
        async def approve_cleep_handler(msg: Message, bot: Bot, state: FSMContext):
            await msg.answer("Напиши сколько боту ждать в секундах прежде чем впустить пользователя в канал,\n"
                             "Когда пользователь нажимает 'Подтвердить' на клавитуре\n"
                             "1 час = 3600 сек.\n"
                             "По умолчанию стоит 10 сек\n"
                             "Ввод данных перезаписывает предыдущее значение")
            await state.set_state(Form.add_wait_for_approve)
        @self.join_handler.router.message(Form.add_wait_for_approve)
        async def approve_cleepo(msg: Message, state: FSMContext, bot: Bot):
            self.join_handler.wait_for_approve = int(msg.text)
            await msg.answer(f"Вы установили {self.join_handler.wait_for_approve}")
            bot_info = await bot.get_me()
            bot_id = bot_info.id
            await save_string_to_file("wait_for_approve"+"#"+str(self.join_handler.wait_for_approve), f"settings/{bot_id}.txt")
            await state.clear()