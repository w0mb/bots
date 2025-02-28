from aiogram import Bot
from aiogram.filters import Command
from aiogram.types import Message

from src_bots.new_privet.handlers.base_handler import BaseHandler
from src_bots.new_privet.utils.file_utils import get_strings_from_file


class GetAllBots(BaseHandler):
    def __init__(self):
        super().__init__()
        self.bot_tokens = []

        @self.router.message(Command(commands=["getallbots"]))
        async def get_command_handler(msg: Message):
            self.bot_tokens = await get_strings_from_file("tokens/tokens.txt")
            bot_info_list = []
            for token in self.bot_tokens:
                bot = Bot(token=token)
                bot_info = await bot.get_me()
                bot_info_list.append(f"@{bot_info.username} (ID: {bot_info.id})")
                await bot.session.close()

            if bot_info_list:
                response = "Список всех ботов:\n" + "\n".join(bot_info_list)
            else:
                response = "Боты не найдены."

            await msg.answer(response)