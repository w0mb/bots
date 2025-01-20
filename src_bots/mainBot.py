import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import subprocess
import os

# Загрузка конфигурации
CONFIG_PATH = "bots_config.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

# Инициализация Telegram бота
BOT_TOKEN = "7322735137:AAG1L8sGPyNqNEIL8henkTsMTWhCIOeWEIE"  # Замените на токен вашего управляющего бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
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

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.reply("Добро пожаловать в бот-менеджер!\nДоступные команды:\n"
                        "/start - Запустить бота\n"
                        "/stop - Остановить бота\n"
                        "/status - Проверить статус ботов")


@dp.message_handler(commands=["status"])
async def status_command(message: types.Message):
    statuses = await check_status()
    await message.reply(f"Статус ботов:\n{statuses}")


@dp.message_handler(commands=["start_bot"])
async def start_bot_command(message: types.Message):
    args = message.get_args()
    if not args:
        await message.reply("Укажите имя бота. Пример: /start_bot Bot1")
        return

    bot_name = args.strip()
    bot_config = next((bot for bot in config["bots"] if bot["name"] == bot_name), None)
    if not bot_config:
        await message.reply(f"Бот с именем {bot_name} не найден.")
        return

    if bot_name in processes:
        await message.reply(f"Бот {bot_name} уже запущен.")
        return

    result = await run_bot(bot_config)
    if isinstance(result, str):
        await message.reply(result)
    else:
        await message.reply(f"Бот {bot_name} успешно запущен.")


@dp.message_handler(commands=["stop_bot"])
async def stop_bot_command(message: types.Message):
    args = message.get_args()
    if not args:
        await message.reply("Укажите имя бота. Пример: /stop_bot Bot1")
        return

    bot_name = args.strip()
    result = await stop_bot(bot_name)
    await message.reply(result)


# Планировщик задач
async def scheduled_task():
    statuses = await check_status()
    print(f"Проверка статуса ботов:\n{statuses}")


if __name__ == "__main__":
    scheduler.add_job(scheduled_task, "interval", minutes=120)  # Каждые 10 минут проверяет статусы
    scheduler.start()

    print("Бот-менеджер запущен.")
    executor.start_polling(dp, skip_updates=True)
