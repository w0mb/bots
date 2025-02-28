from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class Keyboard:
    def __init__(self):
        self.buttons = [[InlineKeyboardButton(text="Подтвердить", callback_data="confirm")]]  # Базовая кнопка

    def add_link(self, text: str, invite_link: str):
        """Добавляет кнопку с ссылкой, если передана корректная строка."""
        if isinstance(invite_link, str) and invite_link.startswith("http"):
            self.buttons.insert(0, [InlineKeyboardButton(text=text, url=invite_link)])

    def get_keyboard(self) -> InlineKeyboardMarkup:
        """Возвращает инлайн-клавиатуру."""
        return InlineKeyboardMarkup(inline_keyboard=self.buttons)

