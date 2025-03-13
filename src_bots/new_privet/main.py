import asyncio
import logging

from bot_factory import BotFactory
from utils.file_utils import get_strings_from_file

async def main():
    bot_factory = BotFactory()

    BOT_TOKENS = await get_strings_from_file("tokens/tokens.txt")

    for token in BOT_TOKENS:
        bot, dp = await bot_factory.create_bot(token)
        if bot and dp:
            await bot_factory.start_polling(bot, dp)

    await asyncio.gather(*bot_factory.tasks)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())