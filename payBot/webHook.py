from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, Update
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from contextlib import asynccontextmanager

BOT_TOKEN = "7414957579:AAEYqGD3OTcp4DxfHud6NOJJU8zYlWeIHvU"

# Создаем бота с DefaultBotProperties для установки parse_mode
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Обработчик команды /start
@dp.message(CommandStart())
async def start_command_handler(message: Message):
    await message.answer("Привет! Это простой бот для тестирования вебхуков.")

# Контекстный менеджер для настройки и удаления вебхука
@asynccontextmanager
async def lifespan(app: FastAPI):
    webhook_url = "https://193.124.117.17/webhook"  # Укажите ваш вебхук-URL
    await bot.set_webhook(
        url=webhook_url,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True,
    )
    yield
    await bot.delete_webhook()

# Создаем приложение FastAPI
app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")

# Страница для корневого пути
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Обработчик вебхуков
@app.post("/webhook")
async def webhook(request: Request):
    try:
        # Получаем данные из POST запроса
        data = await request.json()
        
        # Создаем объект обновления
        update = Update.model_validate(data)

        # Обрабатываем обновление
        await dp.feed_update(bot, update)

        return {"status": "ok"}
    except Exception as e:
        # Обработка ошибок
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Запуск FastAPI приложения с SSL
    uvicorn.run(app, host="0.0.0.0", port=8080, ssl_certfile="../sertificates/server.crt", ssl_keyfile="../sertificates/server.key")
