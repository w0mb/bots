from aiogram import Bot
from aiogram.filters import Command
from aiogram.types import Message

from src_bots.new_privet.handlers.base_handler import BaseHandler


class GetCommandHendler(BaseHandler):
    def __init__(self):
        super().__init__()

        @self.router.message(Command(commands=["getcommands"]))
        async def get_command_handler(msg: Message, bot: Bot):
            await msg.answer(
                "📋 *Список всех доступных команд:*\n\n"
                "🔧 *Основные команды*\n"
                "/getcommands - 📜 Показать список всех доступных команд\n"
                "/getallbots - 🤖 Получить список всех ботов в системе\n"
                "/delbot - 🗑️ Удалить бота из системы по его username\n"
                "/check - 🔍 Получить имя и ID бота\n\n"
                "📨 *Управление заявками*\n"
                "/approvesleep - ⏳ Установить задержку перед принятием в канал (в секундах)\n"
                "/addsleep - ⏱️ Установить задержку между спам-сообщениями (по умолчанию = 3600 секунд)\n"
                "/spamtype - 📩 Выбрать тип спама: `both`, `only_text`, `only_pic` (по умолчанию = both)\n\n"
                "🖲️ *Управление кнопками*\n"
                "/addlink - ➕ Добавить кнопку с ссылкой\n"
                "/dellink - ➖ Удалить кнопку с ссылкой\n"
                "/getlinks - 📂 Получить список всех кнопок с ссылками\n"
                "/dellinkall - 🗑️ Удалить всю клавиатуру (кроме кнопки *Подтвердить*)\n\n"
                "📂 *Управление каналами*\n"
                "/getchanels - 📜 Показать список всех каналов и их ботов\n"
                "/getbotchannels - 🤖 Показать список каналов бота по его username\n"
                "/setaccepttype - ⚙️ Установить каналу значение `True` или `False` для автопринятия заявок\n\n"
                "ℹ️ *Примечание:*\n"
                "*ведется разработка*",
                parse_mode="Markdown"
            )


