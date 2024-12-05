import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from config import TOKEN
from bot import bot, dp  # Импортируем уже инициализированные bot и dp

CERT_PATH = "../sertificates/server.crt"
KEY_PATH = "../sertificates/server.key"

# Старт вебхука
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


# Основная функция для запуска задач
async def main():
    print("Бот стартанул")

    # Создаем задачи для всех функций
    tasks = [
        asyncio.create_task(start_webhook())  # Задача для вебхука
    ]
    
    # Запускаем все задачи до завершения
    await asyncio.gather(*tasks)

# Для Python 3.7+ используем asyncio.run
if __name__ == '__main__':
    asyncio.run(main())
