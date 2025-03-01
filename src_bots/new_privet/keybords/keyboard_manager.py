from src_bots.new_privet.keybords.keybord import Keyboard
from src_bots.privet.utils import get_strings_from_file


class KeyboardManager:
    def __init__(self):
        self.keyboards = {}

    async def get_keyboard(self, bot_id: int):
        """Получить клавиатуру для бота по его ID. Если её нет, создать новую."""
        if bot_id not in self.keyboards:
            self.keyboards[bot_id] = Keyboard()
            await self.load_buttons_from_file(bot_id)  # Загружаем кнопки из файла
        return self.keyboards[bot_id]

    async def add_link(self, bot_id: int, text: str, invite_link: str):
        """Добавить ссылку в клавиатуру для бота."""
        keyboard = await self.get_keyboard(bot_id)
        keyboard.add_link(text, invite_link)

    def delete_link(self, bot_id: int, text: str, invite_link: str):
        """Удалить ссылку из клавиатуры для бота."""
        if bot_id in self.keyboards:
            self.keyboards[bot_id].delete_link(text, invite_link)

    def remove_keyboard(self, bot_id: int):
        """Удалить клавиатуру для бота."""
        if bot_id in self.keyboards:
            del self.keyboards[bot_id]

    async def load_buttons_from_file(self, bot_id: int):
        """Загрузить кнопки из файла и добавить их в клавиатуру."""
        file_path = f"keybords/{bot_id}.txt"
        try:
            lines = await get_strings_from_file(file_path)
            for line in lines:
                if "$" in line:  # Проверяем, что строка содержит разделитель
                    text, url = line.strip().split("$", 1)  # Разделяем текст и URL
                    await self.add_link(bot_id, text, url)  # Добавляем кнопку
        except FileNotFoundError:
            print(f"Файл {file_path} не найден. Кнопки не загружены.")