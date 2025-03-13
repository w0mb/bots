from aiogram import Bot
from aiogram.filters import Command
from aiogram.types import Message

from handlers.base_handler import BaseHandler


class Test(BaseHandler):
    def __init__(self):
        super().__init__()
        @self.router.message(Command(commands=['check']))
        async def test(msg: Message, bot: Bot):
            bot_info = await bot.get_me()

            await msg.answer("Привет я ботик\n"
                             f"мой id {bot_info.id}\n"
                             f"мое имя {bot_info.username}")