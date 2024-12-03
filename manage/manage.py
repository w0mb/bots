import asyncio
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.types import ContentType, Message

API_TOKEN = '8095946793:AAGMe2EOGaEjNB0t9coZ6aW3ktD6qp_wdjM'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

# Регистрируем роутер в диспетчере
dp.include_router(router)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 МБ в байтах

@router.message(F.photo | F.document)
async def process_media(message: Message):
    file = None
    # Если сообщение содержит фото
    if message.photo:
        file = message.photo[-1]  # Берем последнее (наивысшего качества)
    # Если сообщение содержит документ
    elif message.document:
        file = message.document
    
    # Если файл определен
    if file:
        file_info = await bot.get_file(file.file_id)
        
        # Получаем размер файла в байтах
        file_size = file_info.file_size

        # Проверяем, что размер файла не превышает допустимый
        if file_size > MAX_FILE_SIZE:
            await message.answer("Файл слишком большой. Пожалуйста, выберите файл меньше 10 МБ.")
            return

        # Если файл в пределах допустимого размера, скачиваем его
        destination_path = f"{file.file_id}.jpg" if message.photo else file.file_name
        await bot.download(file.file_id, destination=destination_path)
        await message.answer("Файл успешно загружен.")

        # Получаем информацию о пользователе
        username = message.from_user.username or message.from_user.first_name or f"ID: {message.from_user.id}"
        caption = f"Отправлено пользователем: @{username}" if message.from_user.username else f"Отправлено пользователем: {username}"

        # Отправляем файл с подписью
        if message.photo:
            # Отправляем фото с подписью
            await bot.send_photo(chat_id='5218810364', photo=file.file_id, caption=caption)
        elif message.document:
            # Отправляем документ с подписью
            await bot.send_document(chat_id='5218810364', document=file.file_id, caption=caption)
    else:
        await message.answer("Отправленный файл не поддерживается.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("Бот стартовал")
    asyncio.run(main())
