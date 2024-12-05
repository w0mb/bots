import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

API_TOKEN = "7378367346:AAHdke_WxuNo3diBp2bQvQStdgGqKIT3gfY"  # Укажите свой токен

CERT_PATH = "../sertificates/server.crt"
KEY_PATH = "../sertificates/server.key"

# Создаем бота и диспетчер
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer("Привет! Это тестовый вебхук.")

# Обработчик запуска бота
@dp.startup.register
async def on_startup(bot: Bot):
    print("Бот успешно запущен!")

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

# Основная функция
async def main():
    print("Бот стартанул")

    # Параллельно запускаем long polling и webhook
    webhook_task = asyncio.create_task(start_webhook())
    
    await asyncio.gather(webhook_task)

if __name__ == "__main__":
    asyncio.run(main())
