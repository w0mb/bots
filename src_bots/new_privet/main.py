import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from src_bots.new_privet.bot_factory import BotFactory
from src_bots.new_privet.utils.file_utils import get_strings_from_file

async def main():
    # Инициализация фабрики ботов
    bot_factory = BotFactory()

    # Загрузка токенов из файла
    BOT_TOKENS = await get_strings_from_file("tokens/tokens.txt")

    # Создание ботов и диспетчеров
    for token in BOT_TOKENS:
        bot, dp = await bot_factory.create_bot(token)
        if bot and dp:
            # Запуск пуллинга
            await bot_factory.start_polling(bot, dp)

    # Ожидание завершения задач
    await asyncio.gather(*bot_factory.tasks)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())