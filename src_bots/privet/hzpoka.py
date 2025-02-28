import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
import asyncio

from utils import get_strings_from_file
from accept_handler import accept_handler

async def main():
    BOT_TOKENS = await get_strings_from_file("tokens.txt")

    bots = [
        Bot(
            token=token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        for token in BOT_TOKENS
    ]

    dispatchers = [Dispatcher() for _ in bots]
    tasks = []

    # Передаем списки в контекст бота
    for bot, dp in zip(bots, dispatchers):
        bot.__dict__["bots"] = bots
        bot.__dict__["dispatchers"] = dispatchers
        bot.__dict__["tasks"] = tasks

        router = accept_handler
        dp.include_router(router)

    logging.basicConfig(level=logging.INFO)

    for i, (bot, dp) in enumerate(zip(bots, dispatchers)):
        try:
            await bot.delete_webhook(drop_pending_updates=True)

            task = asyncio.create_task(dp.start_polling(bot))
            tasks.append(task)
            logging.info(f"Бот {i + 1} запущен")
        except Exception as e:
            logging.error(f"Ошибка при запуске бота {i + 1}: {e}")

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())