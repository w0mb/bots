import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiogram.types import Message
from config import API_TOKEN  # Убедитесь, что ваш токен прописан в config.py

CERT_PATH = "../sertificates/server.crt"
KEY_PATH = "../sertificates/server.key"

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Обработчик команды /start
async def send_welcome(message: Message):
    await message.answer("Привет! Это тестовый вебхук.")

# Регистрация обработчика команды
dp.message.register(send_welcome, Command("start"))

# Старт вебхука
async def start_webhook():
    try:
        app = web.Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
        print("Starting webhook server...")

        # Используем текущий цикл событий
        current_loop = asyncio.get_event_loop()
        await web.run_app(
            app,
            host="0.0.0.0",
            port=8443,
            ssl_context={"certfile": CERT_PATH, "keyfile": KEY_PATH},
            loop=current_loop  # Используем существующий цикл
        )
    except Exception as e:
        print(f"Error starting webhook server: {e}")

# Запуск вебхука с уже существующим циклом событий
if __name__ == "__main__":
    print("Бот стартанул")
    asyncio.run(start_webhook())  # asyncio.run будет корректно работать с текущим циклом
