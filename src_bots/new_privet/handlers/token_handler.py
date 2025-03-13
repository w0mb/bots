from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from interface_bot_factory import IBotFactory
from utils.file_utils import save_string_to_file
from handlers.base_handler import BaseHandler

class TokenHandler(BaseHandler):
    class TokenState(StatesGroup):
        waiting_for_token = State()

    def __init__(self, bot_factory: IBotFactory):
        super().__init__()
        self.bot_factory = bot_factory

        @self.router.message(Command(commands=['addtoken']))
        async def add_token_handler(message: Message, state: FSMContext):
            await message.answer("Пришли мне токен, чтобы я добавил его в систему.")
            await state.set_state(self.TokenState.waiting_for_token)

        @self.router.message(self.TokenState.waiting_for_token)
        async def add_token_handler1(message: Message, bot: Bot, state: FSMContext):
            new_token = message.text.strip()
            if new_token:
                await save_string_to_file(new_token, "tokens/tokens.txt")

                new_bot, new_dp = await self.bot_factory.create_bot(new_token)
                if new_bot and new_dp:
                    await self.bot_factory.start_polling(new_bot, new_dp)
                    await message.answer("Токен успешно добавлен, и бот запущен!")
                    await state.clear()
                    return
            else:
                await message.answer("Токен не может быть пустым.")
                await state.clear()