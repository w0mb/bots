import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, Update
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from contextlib import asynccontextmanager

# Telegram Bot Token
BOT_TOKEN = "7378367346:AAHdke_WxuNo3diBp2bQvQStdgGqKIT3gfY"
WEBHOOK_URL = "https://193.124.117.17/webhook"  # Например, https://example.com/webhook

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Настройка FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Настройка вебхука при старте
    await bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)
    yield
    # Удаление вебхука при завершении
    await bot.delete_webhook()

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Обработчик команды /start
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет! Я работаю через вебхуки.")


# Корневая страница (если хотите использовать веб-интерфейс)
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Webhook endpoint
@app.post("/webhook")
async def webhook(request: Request):
    try:
        # Обработка обновления от Telegram
        update = Update.model_validate(await request.json(), context={"bot": bot})
        await dp.feed_update(bot, update)
        return {"status": "ok"}
    except Exception as e:
        logging.error(f"Ошибка обработки вебхука: {e}")
        return {"status": "error"}


# Запуск приложения
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=u"%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    uvicorn.run(app, host="0.0.0.0", port=8443)
