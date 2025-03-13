from aiogram import Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from handlers.base_handler import BaseHandler
from handlers.helpers.join_funcs import update_channel_file
from interface_bot_factory import IBotFactory
from utils.file_utils import remove_string_from_file


class DeleteBot(BaseHandler):
    def __init__(self, bot_factory: IBotFactory):
        super().__init__()
        self.bot_factory = bot_factory

        class Form(StatesGroup):
            del_bot = State()
        @self.router.message(Command(commands=["delbot"]))
        async def del_bot_handler(msg: Message, state: FSMContext):
            await msg.answer("введите username бота чтобы удалить его из системы(это действие удалит его токен тоже)")
            await state.set_state(Form.del_bot)
            @self.router.message(Form.del_bot)
            async def del_bot(msgg: Message, state: FSMContext, bot: Bot):
                try:
                    bot_username = msgg.text
                    target_bot = await bot_factory.get_bot_by_username(bot_username)
                    target_dp = await bot_factory.get_dispatcher_by_bot(target_bot)
                    await update_channel_file(None, None,"left", target_bot)
                    await remove_string_from_file(target_bot.token, "tokens/tokens.txt")
                    await self.bot_factory.stop_pooling(target_bot, target_dp)
                    await msgg.answer(f"Бот @{msgg.text} успешно удален из системы.")
                except Exception as e:
                    await msgg.answer(f"Ошибка при удалении бота: {e}")
                finally:
                    await state.clear()