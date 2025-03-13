import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import logging

from handlers.CommandHandlers import CommandHandlers
from handlers.RateLimitingMiddleware import RateLimitingMiddleware
from handlers.bot_add_to_channel_handler import BotAddToChannelHandler
from handlers.delete_bot_handler import DeleteBot
from handlers.get_all_bots_handler import GetAllBots
from handlers.get_channels_handler import GetChannelsHandler
from handlers.join_handler import JoinHandler
from handlers.link_handler import LinkHandler
from handlers.get_commands_handler import GetCommandHendler
# from handlers.public_join_handler import PublicJoinHandler
from handlers.token_handler import TokenHandler
from handlers.test_handler import Test
from interface_bot_factory import IBotFactory
from keybords.keyboard_manager import KeyboardManager


class BotFactory(IBotFactory):
    def __init__(self):
        self.bots = []
        self.dispatchers = []
        self.tasks = []

    async def _register_handlers(self, dp: Dispatcher):
        ids = []
        keyboard_manager = KeyboardManager()

        token_handler = TokenHandler(self)
        delete_bot_handler = DeleteBot(self)
        get_channels_handler = GetChannelsHandler(self)
        bot_add_to_channel_handler = BotAddToChannelHandler()
        command_handler = GetCommandHendler()
        # public_join_handler = PublicJoinHandler(keyboard_manager)
        link_handler = LinkHandler(keyboard_manager)

        join_handler = JoinHandler(keyboard_manager, self)
        await join_handler.initialize()

        test_handler = Test()
        get_all_bots_handler = GetAllBots()
        commands_handlers = CommandHandlers(join_handler)

        dp.include_router(test_handler.get_router())
        dp.include_router(token_handler.get_router())
        dp.include_router(link_handler.get_router())
        dp.include_router(join_handler.get_router())
        dp.include_router(command_handler.get_router())
        dp.include_router(get_all_bots_handler.get_router())
        dp.include_router(delete_bot_handler.get_router())
        dp.include_router(get_channels_handler.get_router())
        # dp.include_router(public_join_handler.get_router())
        dp.include_router(bot_add_to_channel_handler.get_router())
        dp.include_router(commands_handlers.get_router())

    async def create_bot(self, token: str):

        try:
            bot = Bot(
                token=token,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
            dp = Dispatcher()
            dp.message.middleware(RateLimitingMiddleware())
            dp.callback_query.middleware(RateLimitingMiddleware())
            await self._register_handlers(dp)

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
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            task = asyncio.create_task(dp.start_polling(bot))
            self.tasks.append(task)
            logging.info(f"Бот с токеном {bot.token} запущен.")
        except Exception as e:
            logging.error(f"Ошибка при запуске бота: {e}")

    async def stop_pooling(self, bot: Bot, dp: Dispatcher):
        try:
            await dp.stop_polling()
            for task in self.tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                    self.tasks.remove(task)
                    break
            await bot.session.close()
            logging.info(f"Бот с токеном {bot.token} остановлен.")
        except Exception as e:
            logging.error(f"Ошибка при остановке бота: {e}")

    async def get_dispatcher_by_bot(self, bot: Bot) -> Dispatcher | None:
            for i, b in enumerate(self.bots):
                if b.token == bot.token:
                    return self.dispatchers[i]
            return None

    async def get_bot_by_username(self, username: str) -> Bot | None:
        for i, b in enumerate(self.bots):
            bot_info = await b.get_me()
            if bot_info.username == username:
                return self.bots[i]
        return None
    async def get_all_pooling_bots(self) -> list[Bot] | None:
        try:
            return self.bots
        except Exception:
            return None

    async def get_all_polling_bots_ids(self) -> list[int] | None:
        try:
            bot_ids = []
            for bot in self.bots:
                bot_info = await bot.get_me()
                bot_ids.append(bot_info.id)
            return bot_ids
        except Exception as e:
            logging.error(f"Ошибка при получении ID ботов: {e}")
            return None