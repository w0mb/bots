from aiogram import Bot
from aiogram.filters import Command
from aiogram.types import Message

from src_bots.new_privet.handlers.base_handler import BaseHandler


class GetCommandHendler(BaseHandler):
    def __init__(self):
        super().__init__()

        @self.router.message(Command(commands=["getcommands"]))
        async def get_command_handler(msg: Message, bot: Bot):
            await msg.answer("список всех доступных команд:\n"
                       "/getcommands - список все доступных команд\n"
                       "/addsleep - добавить задержку спама(дефолт=3600мс)\n"
                       "/spamtype - выбрать тип спама(дефолт=оба)\n"
                       "/addlink - добавить кнопку с ссылкой\n"
                       "/dellink - удалить кнопку с ссылкой\n"
                       "/getlinks - получить все кнопки с ссылками\n"
                       "/check - получить имя и id бота\n"
                       "/approvesleep - добавить задержку перед принятием в канал\n"
                       "/getallbots - получить список всех ботов")

