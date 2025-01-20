import json
import asyncio
from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import subprocess
import os
from datetime import datetime
from aiogram.filters import Command

# Загрузка конфигурации
CONFIG_PATH = "bots_config.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

# Инициализация Telegram бота
router = Router()
BOT_TOKEN = "7322735137:AAG1L8sGPyNqNEIL8henkTsMTWhCIOeWEIE"  # Замените на токен вашего управляющего бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)
# Инициализация планировщика
scheduler = AsyncIOScheduler()

# Словарь для отслеживания процессов
processes = {}


async def run_bot(bot_config):
    """Запуск бота из конфигурации."""
    script_path = bot_config["script_path"]
    args = bot_config.get("args", [])

    try:
        process = await asyncio.create_subprocess_exec(
            "python", script_path, *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        processes[bot_config["name"]] = process
        return process
    except Exception as e:
        return f"Ошибка запуска {bot_config['name']}: {e}"


async def stop_bot(bot_name):
    """Остановка бота."""
    process = processes.get(bot_name)
    if process and process.returncode is None:  # Проверка, что процесс активен
        process.terminate()
        await process.wait()
        processes.pop(bot_name)
        return f"Бот {bot_name} остановлен."
    return f"Бот {bot_name} уже остановлен или не запущен."


async def check_status():
    """Проверка статуса всех ботов."""
    statuses = []
    for bot in config["bots"]:
        name = bot["name"]
        process = processes.get(name)
        status = "Работает" if process and process.returncode is None else "Не работает"
        statuses.append(f"{name}: {status}")
    return "\n".join(statuses)


# Команды Telegram бота
@router.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Добро пожаловать в бот-менеджер!\nДоступные команды:\n"
                         "/start - Запустить бота\n"
                         "/stop - Остановить бота\n"
                         "/status - Проверить статус ботов")


@router.message(Command("status"))
async def status_command(message: Message):
    statuses = await check_status()
    await message.answer(f"Статус ботов:\n{statuses}")


@router.message(Command("start_bot"))
async def start_bot_command(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Укажите имя бота. Пример: /start_bot Bot1")
        return

    bot_name = args[1].strip()
    bot_config = next((bot for bot in config["bots"] if bot["name"] == bot_name), None)
    if not bot_config:
        await message.answer(f"Бот с именем {bot_name} не найден.")
        return

    if bot_name in processes:
        await message.answer(f"Бот {bot_name} уже запущен.")
        return

    result = await run_bot(bot_config)
    if isinstance(result, str):
        await message.answer(result)
    else:
        await message.answer(f"Бот {bot_name} успешно запущен.")


@router.message(Command("stop_bot"))
async def stop_bot_command(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Укажите имя бота. Пример: /stop_bot Bot1")
        return

    bot_name = args[1].strip()
    result = await stop_bot(bot_name)
    await message.answer(result)


# Планировщик задач
async def scheduled_task():
    statuses = await check_status()
    print(f"Проверка статуса ботов:\n{statuses}")


async def main():
    # Инициализация планировщика
    scheduler.add_job(scheduled_task, "interval", minutes=120)  # Каждые 120 минут проверяет статусы
    scheduler.start()

    print("Бот-менеджер запущен.")
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
