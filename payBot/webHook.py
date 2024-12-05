import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

API_TOKEN = "7378367346:AAHdke_WxuNo3diBp2bQvQStdgGqKIT3gfY"  # Замените на свой токен

CERT_PATH = "../sertificates/server.crt"
KEY_PATH = "../sertificates/server.key"

# Инициализация бота и диспетчера
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

# Основная функция для старта вебхука
async def start_webhook():
    try:
        # Удаляем старый Webhook
        await bot.delete_webhook(drop_pending_updates=True)

        # Устанавливаем новый Webhook
        await bot.set_webhook(url="https://ваш-домен/webhook")

        # Создаем приложение AIOHTTP
        app = web.Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
        print("Starting webhook server...")

        # Запускаем сервер с SSL
        ssl_context = {
            "certfile": CERT_PATH,
            "keyfile": KEY_PATH,
        }
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host="0.0.0.0", port=8443, ssl_context=ssl_context)
        await site.start()

        print("Webhook server started successfully!")
        # Ожидаем завершения работы
        await asyncio.Event().wait()
    except Exception as e:
        print(f"Error starting webhook server: {e}")

# Основная функция
async def main():
    print("Бот стартанул")
    # Запускаем Webhook
    await start_webhook()

if __name__ == "__main__":
    # Используем asyncio.run для запуска основного приложения
    asyncio.run(main())
