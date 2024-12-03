import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ChatJoinRequest
import json
#😈PREMIUM Слитые ссучки PREMIUM😈
#@test_oplata_bot
API_TOKEN = '8188712922:AAHyTWd6xgxOwEbYTS7oAlLNl-2_oLOleyQ'
CHAT_ID = -1002248182741
DAILY_LIMIT = 500

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Файл для хранения данных о заявках
DATA_FILE = 'join_requests.json'

# Загружаем данные из файла
def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {'count': 0, 'last_reset': str(datetime.now().date())}
    return data

# Сохраняем данные в файл
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# Обновление счётчика
def update_request_count():
    data = load_data()
    today = str(datetime.now().date())

    # Сброс счётчика, если наступил новый день
    if data['last_reset'] != today:
        data = {'count': 0, 'last_reset': today}

    data['count'] += 1
    save_data(data)
    return data['count']

@dp.chat_join_request(F.chat.id == CHAT_ID)
async def auto_approve_join_request(update: ChatJoinRequest, bot: Bot):
    try:
        current_count = update_request_count()

        # Проверяем лимит
        if current_count > DAILY_LIMIT:
            print(f"Лимит заявок достигнут: {current_count}")
            return

        await bot.approve_chat_join_request(chat_id=update.chat.id, user_id=update.from_user.id)
        print(f"Заявка от {update.from_user.id} одобрена. Текущее количество: {current_count}")
    except Exception as e:
        print(f"Ошибка при одобрении заявки: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
