import asyncio

from aiogram import Bot, Dispatcher

from config import PayBotConfig
from bot import router_message
config = PayBotConfig

async def main():
    bot = Bot(token=config.token)
    dp = Dispatcher()

    dp.include_routers(router_message)

    # Альтернативный вариант регистрации роутеров по одному на строку
    # dp.include_router(questions.router)
    # dp.include_router(different_types.router)

    # Запускаем бота и пропускаем все накопленные входящие
    # Да, этот метод можно вызвать даже если у вас поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())