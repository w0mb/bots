import logging
from pathlib import Path

from keybords.keybord import Keyboard
from utils.file_utils import get_strings_from_file, remove_string_from_file, save_string_to_file


class KeyboardManager:
    def __init__(self):
        self.keyboards = {}

    async def get_keyboard(self, bot_id: int):
        if bot_id not in self.keyboards:
            self.keyboards[bot_id] = Keyboard()
            await self.load_buttons_from_file(bot_id)
        return self.keyboards[bot_id]

    async def add_link(self, bot_id: int, text: str, invite_link: str):
        self.keyboards[bot_id].add_link(text, invite_link)

    async def delete_link(self, bot_id: int, text: str, invite_link: str, channel_id: str):
        try:
            await remove_string_from_file(f"keybords/{bot_id}.txt", f"{text}${invite_link}${channel_id}")
            if bot_id in self.keyboards:
                self.keyboards[bot_id].delete_link(text, invite_link)
        except Exception as e:
            logging.error(f"Ошибка при удалении delete_link: {e}")
    async def remove_keyboard(self, bot_id: int):
        await remove_string_from_file(f"keybords/{bot_id}.txt", None)
        if bot_id in self.keyboards:
            del self.keyboards[bot_id]

    async def load_buttons_from_file(self, bot_id: int):
        try:
            lines = await get_strings_from_file(f"keybords/{bot_id}.txt")
            if lines is not None:
                for line in lines:
                    if "$" in line:
                        parts = line.strip().split("$", 3)
                        if parts[0].strip() and parts[2].strip():
                            text = parts[0]
                            url = parts[1]
                            await self.add_link(bot_id, text, url)
        except FileNotFoundError:
            print(f"Файл keybords/{bot_id}.txt не найден. Кнопки не загружены. - load_buttons_from_file")

    async def save_buttons_to_file(self, bot_id: int, text: str) -> bool:
        parts = text.split("$")

        if len(parts) < 3:
            logging.warning("Некорректный формат строки, ожидалось 'Текст$URL$channel_id'")
            return False

        text_part, _, channel_id = parts

        if text_part.strip() and channel_id.strip().startswith("-100"):
            try:
                await save_string_to_file(text, f"keybords/{bot_id}.txt")
                return True
            except Exception as e:
                logging.error(f"Ошибка при сохранении кнопок в файл keybords/{bot_id}.txt: {e}")
                return False
        else:
            logging.error(f"Текст или channel_id не корректны")
            return False
