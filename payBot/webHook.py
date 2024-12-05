from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from contextlib import asynccontextmanager

BOT_TOKEN = "7378367346:AAHdke_WxuNo3diBp2bQvQStdgGqKIT3gfY"

# Используем DefaultBotProperties для установки parse_mode
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


@dp.message(CommandStart())
async def start_command_handler(message: Message):
    await message.answer("Привет! Это простой бот для тестирования вебхуков.")


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


# Настройки FastAPI
app = FastAPI(lifespan=lifespan)
# app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = dp.resolve_update(data)
    await dp.feed_update(bot, update)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, ssl_certfile="../sertificates/server.crt", ssl_keyfile="../sertificates/server.key")
