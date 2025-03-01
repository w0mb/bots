from pathlib import Path

from aiogram import Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup

from src_bots.new_privet.handlers.base_handler import BaseHandler
from src_bots.new_privet.interface_bot_factory import IBotFactory
from src_bots.privet.utils import get_strings_from_file


class GetChannelsHandler(BaseHandler):
    def __init__(self, bot_factory: IBotFactory):
        super().__init__()
        self.bot_factory = bot_factory
        class Form(StatesGroup):
            bot_username_state = State()
            add_accept_type = State()

        @self.router.message(Command(commands=["getchanels"]))
        async def get_all_chanels_handler(msg: Message):
            bot_list = await bot_factory.get_all_pooling_bots()
            result_dict = {}

            # Создаем словарь соответствий bot_id -> bot_username
            bot_id_to_username = {}

            for bot in bot_list:
                bot_info = await bot.get_me()  # Получаем информацию о боте
                bot_id_to_username[str(bot_info.id)] = f"@{bot_info.username}" if bot_info.username else f"Unknown({bot_info.id})"

            # Теперь читаем файлы и заменяем bot_id на username
            for bot in bot_list:
                try:

                    channels_list = await get_strings_from_file(f"src_bots/new_privet/bot_channel_ids/{bot.id}.txt")
                    for line in channels_list:
                        parts = line.strip().split(":")
                        if len(parts) >= 3:
                            title, bot_id = parts[1], parts[2]  # bot_id из файла (строка)
                            # Если bot_id найден в словаре, заменяем его на username
                            bot_username = bot_id_to_username.get(bot_id, f"Unknown({bot_id})")
                            result_dict[title] = bot_username
                except FileNotFoundError:
                    print(f"Файл не найден.")

            # Преобразуем словарь в строку формата "Название - @bot_username"
            formatted_result = "\n".join([f"{title} - {bot_username}" for title, bot_username in result_dict.items()])

            await msg.answer(formatted_result if formatted_result else "Нет данных.")

        @self.router.message(Command(commands=["getbotchannels"]))
        async def get_chanels_handler(msg: Message, state: FSMContext):
            await msg.answer("Введите username бота")
            await state.set_state(Form.bot_username_state)

        @self.router.message(Form.bot_username_state)
        async def get_channels(msg: Message, state: FSMContext):
            bot_username = msg.text
            target_bot = await bot_factory.get_bot_by_username(bot_username)

            if target_bot is None:
                await state.clear()
                return

            bot_info = await target_bot.get_me()

            try:
                channels_list = await get_strings_from_file(f"src_bots/new_privet/bot_channel_ids/{bot_info.id}.txt")
            except FileNotFoundError:
                await msg.answer(f"Файл для бота @{bot_username} не найден.")
                await state.clear()
                return

            result_list = []
            for line in channels_list:
                parts = line.strip().split(":")
                result_list.append(parts[1])
            response = "\n".join(result_list) if result_list else "Нет данных."
            await msg.answer(response)
            await state.clear()

        @self.router.message(Command(commands=["setaccepttype"]))
        async def set_accept_type_handler(msg: Message, state:FSMContext):
            await msg.answer("Использование: channel_id:True/False")
            await state.set_state(Form.add_accept_type)
        @self.router.message(Form.add_accept_type)
        async def set_accept_type(msg: Message, bot: Bot, state: FSMContext):
            args = msg.text.strip().split(":")
            if len(args) < 1:
                return
            channel_id = args[0]
            accept_immediately = args[1].lower() == "true"
            base_dir = Path(__file__).parent.parent  # new_privet/
            channel_ids_dir = base_dir / "bot_channel_ids"
            file_path = channel_ids_dir / f"{bot.id}.txt"
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    lines = file.readlines()
                with open(file_path, "w", encoding="utf-8") as file:
                    for line in lines:
                        if line.startswith(channel_id):
                            parts = line.strip().split(":")
                            parts[3] = str(accept_immediately)
                            line = ":".join(parts) + "\n"
                        file.write(line)
                await msg.answer(f"Параметр accept_immediately для канала {channel_id} изменен на {accept_immediately}.")
            except FileNotFoundError:
                await msg.answer("Файл с каналами не найден.")
            await state.clear()




