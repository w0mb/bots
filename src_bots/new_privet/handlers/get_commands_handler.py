from aiogram import Bot, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.base_handler import BaseHandler
from utils.file_utils import get_strings_from_file


class GetCommandHendler(BaseHandler):
    def __init__(self):
        super().__init__()
        @self.router.message(Command(commands=["getcommands"]))
        async def get_command_handler(msg: Message, bot: Bot):
            await msg.answer(
        "✨ *📋 Список всех доступных команд* ✨\n\n"
    
            "🌟 *🔧 Основные команды* 🌟\n"
            "🚀 /getcommands — *Показать список всех доступных команд*\n"
            "🤖 /getallbots — *Получить список всех ботов в системе*\n"
            "🗑️ /delbot — *Удалить бота из системы по его username*\n"
            "➕ /addtoken — *Добавить бота по его токену*\n"
            "⚙️ /setspamcount — *Установить кол-во спам сообщений у бота*\n"
            "🔍 /check — *Получить имя и ID бота*\n\n"
        
            "📨 *Управление заявками* 📨\n"
            "⏳ /setapprovetime — *Установить задержку перед принятием в канал (не рекомендуется больше 10 сек.)*\n"
            "⏱️ /setsleep — *Установить задержку между спам-сообщениями (по умолчанию 3600 сек.)*\n"
            "📩 /setspamtype — *Выбрать тип спама: `both`, `only_text`, `only_pic`, `creo` (по умолчанию = both)*\n\n"
        
            "🖲️ *Управление кнопками* 🖲️\n"
            "➕ /addlink — *Добавить кнопку с ссылкой*\n"
            "➖ /dellink — *Удалить кнопку с ссылкой*\n"
            "📂 /getlinks — *Получить список всех кнопок с ссылками*\n"
            "🗑️ /dellinkall — *Удалить всю клавиатуру (кроме кнопки «Подтвердить»)*\n\n"
        
            "📂 *Управление каналами* 📂\n"
            "📜 /getchanels — *Показать список всех каналов и их ботов*\n"
            "🤖 /getbotchannels — *Показать список каналов бота по его username*\n"
            "⚙️ /setaccepttype — *Установить каналу `True` или `False` для автопринятия заявок*\n\n"
        
            "🔥 *Крео команды* 🔥\n"
            "🎨 /setkbcreo — *Создать кнопки для крео спама (требуется текст и ссылка)*\n"
            "🎬 /setcaptiontovideocreo — *Установить подпись к видео крео*\n"
            "🎬 /getcaptiontovideocreo — *Получить подпись к видео крео*\n"
            "📹 /setvideocreo — *Установить видео крео*\n"
            "🔑 /setvpusk — *Установить, впускать ли людей в канал крео спама*\n\n"
        
            "🔧 *Команды для ПУБЛИЧНЫХ каналов* 🔧\n"
            "📝 /setwelcomebuttontextpublic — *Установить текст для кнопки приветствия*\n"
            "💬 /setwelcomepublic — *Установить приветственное сообщение для новых подписчиков*\n"
            "🎥 /setwelcomevideopublic — *Установить вступительное видео (заменяет старое)*\n\n"
        
            "ℹ️ *Примечание:* ℹ️\n"
            "💡 *Ведется активная разработка. Следите за обновлениями!* 🚀",
            parse_mode="Markdown"
)

        @self.router.message(Command(commands=["start"]))
        async def start_handler(msg: Message, bot: Bot):
            admins = await get_strings_from_file("admins/admins.txt")
            if str(msg.from_user.id) in admins:
                # Создаем клавиатуру для администраторов
                keyboard = ReplyKeyboardMarkup(
                    keyboard=[
                        [KeyboardButton(text="Команды")]
                    ],
                    resize_keyboard=True  # Опционально: автоматически подгоняет размер клавиатуры
                )
                await msg.answer("Добро пожаловать, администратор!", reply_markup=keyboard)
            else:
                await msg.answer("Добро пожаловать!", reply_markup=types.ReplyKeyboardRemove())  # Убираем клавиатуру для обычных пользователей

        @self.router.message(lambda message: message.text == "Команды")
        async def handle_commands_button(msg: Message, bot: Bot):
            admins = await get_strings_from_file("admins/admins.txt")
            if str(msg.from_user.id) in admins:
                await get_command_handler(msg, bot)
            else:
                await msg.answer("У вас нет доступа к этой команде.")


