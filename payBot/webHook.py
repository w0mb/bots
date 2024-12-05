import asyncio
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from config import bot, dp

CERT_PATH = "../sertificates/server.crt"  # Путь к сертификату
KEY_PATH = "../sertificates/server.key"  # Путь к закрытому ключу

# Функция для запуска вебхука
async def start_webhook():
    try:
        app = web.Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
        print("Starting webhook server...")
        # Запуск веб-сервера с сертификатами
        await web.run_app(
            app,
            host="0.0.0.0",
            port=8443,
            ssl_context={
                "certfile": CERT_PATH,
                "keyfile": KEY_PATH,
            }
        )
    except Exception as e:
        print(f"Error starting webhook server: {e}")