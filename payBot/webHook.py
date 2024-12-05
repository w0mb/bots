import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiogram.types import Message
from config import TOKEN  # Убедитесь, что ваш токен прописан в config.py
from aiogram.filters import Command
CERT_PATH = "../sertificates/server.crt"
KEY_PATH = "../sertificates/server.key"

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer("Привет! Это тестовый вебхук.")

# Старт вебхука
async def start_webhook():
    try:
        # Создаем приложение AIOHTTP
        app = web.Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
        print("Starting webhook server...")

        # Запускаем сервер с использованием SSL
        ssl_context = {
            "certfile": CERT_PATH,
            "keyfile": KEY_PATH,
        }
        await web.run_app(app, host="0.0.0.0", port=8443, ssl_context=ssl_context)
    except Exception as e:
        print(f"Error starting webhook server: {e}")

async def main():
    print("Бот стартанул")

    # Запускаем обработку апдейтов
    dp.startup.register(lambda _: print("Dispatcher startup..."))
    dp.shutdown.register(lambda _: print("Dispatcher shutdown..."))
    await dp.start_polling(bot)  # Если нужно запустить long polling

    # Параллельно запускаем вебхук
    await start_webhook()

if __name__ == "__main__":
    asyncio.run(main())