from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keybords.keyboard_manager import KeyboardManager
from utils.file_utils import save_string_to_file, remove_string_from_file
from handlers.base_handler import BaseHandler

class LinkHandler(BaseHandler):
    def __init__(self, keyboard_manager: KeyboardManager | None):
        super().__init__()
        self.keyboard_manager = keyboard_manager

        class Form(StatesGroup):
            add_link = State()
            del_link = State()

        @self.router.message(Command(commands=['addlink']))
        async def add_link_handler(message: Message, state: FSMContext):
            await message.answer("Пришли текст инлайн-кнопки, её URL, и ID этого канала в одном сообщении через разделитель '$'")
            await state.set_state(Form.add_link)

        @self.router.message(Command(commands=['dellink']))
        async def del_link_handler(message: Message, state: FSMContext):
            await message.answer("Введите текст кнопки, ссылку и ID канала через разделитель '$' если хотите удалить ссылку")
            await state.set_state(Form.del_link)
        @self.router.message(Command(commands=['dellinkall']))
        async def del_link_handler(message: Message, bot: Bot):
            bot_info = await bot.get_me()
            try:
                await keyboard_manager.remove_keyboard(bot_info.id)
                await message.answer("все кнопки с ссылками отчищены")
            except Exception:
                await message.answer("что то пошло не так при удалении клавиатуры")

        @self.router.message(Command(commands=['getlinks']))
        async def get_link_handler(message: Message, bot: Bot):
            bot_info = await bot.get_me()
            bot_id = bot_info.id
            kb = await keyboard_manager.get_keyboard(bot_id)
            await message.answer("твои ссылки", reply_markup=kb.get_keyboard())

        @self.router.message(Form.add_link)
        async def handle_add_link(msg: Message, bot: Bot, state: FSMContext):
            text = msg.text.strip()

            bot_info = await bot.get_me()
            bot_id = bot_info.id

            kb = await keyboard_manager.get_keyboard(bot_id)

            if '$' not in text:
                await msg.answer("Неправильный формат! Используйте разделитель '$' между текстом кнопки и URL.")
                return

            try:
                button_text, invite_url, id = text.split('$', 3)
                await msg.answer(f"Твой текст: {button_text}\nТвоя ссылка: {invite_url}\n твой id:{id}")
                await save_string_to_file(invite_url, f"bot_links/{bot_id}.txt")
                if await keyboard_manager.save_buttons_to_file(bot_id, text.strip()):
                    await keyboard_manager.add_link(bot_id, button_text, invite_url)
                    await msg.answer("Кнопка с ссылкой добавлена!", reply_markup=kb.get_keyboard())
                else:
                    await msg.answer("Ошибка в ваших данных, скорее всего дело в ID или тексте.")
            except ValueError:
                await msg.answer("Ошибка! Убедитесь, что отправили текст в формате: 'Текст кнопки$URL$ID'.")
            finally:
                await state.clear()

        @self.router.message(Form.del_link)
        async def handle_del_link(msg: Message, bot: Bot, state: FSMContext):
            text = msg.text.strip()
            bot_info = await bot.get_me()
            bot_id = bot_info.id
            if '$' not in text:
                await msg.answer("Неправильный формат! Используйте разделитель '$' между текстом кнопки URL и ID.")
                return

            try:
                button_text, invite_url, id = text.split('$', 3)
                await msg.answer(f"Твой текст: {button_text}\nТвоя ссылка: {invite_url}\n твой id {id}")
                await remove_string_from_file(invite_url, f"bot_links/{bot_id}.txt")
                await keyboard_manager.delete_link(bot_id, button_text, invite_url, id)
                await msg.answer("Кнопка с ссылкой удалена!")

            except ValueError:
                await msg.answer("Ошибка! Убедитесь, что отправили текст в формате: 'Текст кнопки$URL$id'.")
            finally:
                await state.clear()
