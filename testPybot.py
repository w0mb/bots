import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from config import TOKEN

# Инициализируем бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Обработчик для команды /start
@dp.message_handler(commands=['start'])
async def start_command(message: Message):
    await message.reply("Привет! Я твой бот. Чем могу помочь?")

# Функция запуска бота
async def main():
    print("Бот запущен")
    await dp.start_polling(bot)

# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())
