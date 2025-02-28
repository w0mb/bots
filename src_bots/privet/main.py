from aiogram import Bot, Dispatcher, Router
import asyncio

from config import TOKEN
from handler import handler_router

bot = Bot(token=TOKEN)
#кароче надо чтобы он отслеживал пдп в тгк и брал новых пдп и писал им спам
#вот кароче покумекать надо над мультиботингом
dp = Dispatcher()
dp.include_router(handler_router)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
