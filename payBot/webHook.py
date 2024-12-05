import asyncio
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from bot import bot, dp  # Импортируем уже инициализированные bot и dp

CERT_PATH = "../sertificates/server.crt"
KEY_PATH = "../sertificates/server.key"

# Старт вебхука
async def start_webhook(loop):
    try:
        app = web.Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
        print("Starting webhook server...")

        # Используем переданный цикл событий (loop)
        await web.run_app(
            app,
            host="0.0.0.0",
            port=8443,
            ssl_context={
                "certfile": CERT_PATH,
                "keyfile": KEY_PATH,
            },
            loop=loop  # Указываем текущий цикл событий
        )
    except Exception as e:
        print(f"Error starting webhook server: {e}")
