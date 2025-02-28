from src_bots.new_privet.keybords.keybord import Keyboard


class KeyboardManager:
    def __init__(self):
        self.keyboards = {}

    def get_keyboard(self, bot_id: int):
        """Получить клавиатуру для бота по его ID. Если её нет, создать новую."""
        if bot_id not in self.keyboards:
            self.keyboards[bot_id] = Keyboard()
        return self.keyboards[bot_id]#Возвращает обьект класса Keyboard(), но для инлайн кнопак нужен InlineMarkup
                                     #А инлайн маркап можно получить в Keyboard().get_keyboard() - пофиксить
    def add_link(self, bot_id: int, text: str, invite_link: str):
        """Добавить ссылку в клавиатуру для бота."""
        keyboard = self.get_keyboard(bot_id)
        keyboard.add_link(text, invite_link)

    def delete_link(self, bot_id: int, text: str, invite_link: str):
        """Удалить ссылку из клавиатуры для бота."""
        if bot_id in self.keyboards:
            self.keyboards[bot_id].delete_link(text, invite_link)

    def remove_keyboard(self, bot_id: int):
        """Удалить клавиатуру для бота."""
        if bot_id in self.keyboards:
            del self.keyboards[bot_id]