import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import logging

from src_bots.new_privet.handlers.get_all_bots_handler import GetAllBots
from src_bots.new_privet.handlers.join_handler import JoinHandler
from src_bots.new_privet.handlers.link_handler import LinkHandler
from src_bots.new_privet.handlers.get_commands_handler import GetCommandHendler
from src_bots.new_privet.handlers.token_handler import TokenHandler
from src_bots.new_privet.handlers.test_handler import Test
from src_bots.new_privet.interface_bot_factory import IBotFactory
from src_bots.new_privet.keybords.keyboard_manager import KeyboardManager


class BotFactory(IBotFactory):
    def __init__(self):
        self.bots = []
        self.dispatchers = []
        self.tasks = []

    def _register_handlers(self, dp: Dispatcher):
        """
        Регистрирует хэндлеры для диспетчера.
        """
        # Создание экземпляров хэндлеров
        keyboard_manager = KeyboardManager()

        token_handler = TokenHandler(self)
        command_handler = GetCommandHendler()
        link_handler = LinkHandler(keyboard_manager)
        join_handler = JoinHandler(keyboard_manager)
        test_handler = Test()
        get_all_bots_handler = GetAllBots()

        # Регистрация роутеров
        dp.include_router(test_handler.get_router())
        dp.include_router(token_handler.get_router())
        dp.include_router(link_handler.get_router())
        dp.include_router(join_handler.get_router())
        dp.include_router(command_handler.get_router())
        dp.include_router(get_all_bots_handler.get_router())

    async def create_bot(self, token: str):
        """
        Создает нового бота и диспетчер.
        """
        try:
            bot = Bot(
                token=token,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
            dp = Dispatcher()

            # Регистрация хэндлеров
            self._register_handlers(dp)

            # Передаем списки в контекст бота
            bot.__dict__["bots"] = self.bots
            bot.__dict__["dispatchers"] = self.dispatchers
            bot.__dict__["tasks"] = self.tasks

            self.bots.append(bot)
            self.dispatchers.append(dp)

            logging.info(f"Бот с токеном {token} создан.")
            return bot, dp
        except Exception as e:
            logging.error(f"Ошибка при создании бота: {e}")
            return None, None

    async def start_polling(self, bot: Bot, dp: Dispatcher):
        """
        Запускает пуллинг для бота.
        """
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            task = asyncio.create_task(dp.start_polling(bot))
            self.tasks.append(task)
            logging.info(f"Бот с токеном {bot.token} запущен.")
        except Exception as e:
            logging.error(f"Ошибка при запуске бота: {e}")