import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ChatJoinRequest
import json

API_TOKEN = "8188712922:AAHyTWd6xgxOwEbYTS7oAlLNl-2_oLOleyQ"
CHAT_IDS = [-1002284058357,-1002248182741]  # Список ID всех групп
DAILY_LIMIT = 500
DATA_FILE = 'join_requests.json'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Функция для загрузки данных
def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {'count': 0, 'last_reset': str(datetime.now().date()), 'pending_requests': []}

    # Гарантируем, что ключи всегда присутствуют
    if 'count' not in data:
        data['count'] = 0
    if 'last_reset' not in data:
        data['last_reset'] = str(datetime.now().date())
    if 'pending_requests' not in data:
        data['pending_requests'] = []

    return data


# Функция для сохранения данных
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# Сброс лимита заявок, если новый день
def update_daily_limit():
    data = load_data()
    today = str(datetime.now().date())

    if data['last_reset'] != today:
        data['count'] = 0
        data['last_reset'] = today
        data['pending_requests'] = []  # Очищаем заявки, если старые уже обработаны
        save_data(data)
    return data

# Добавление заявки в файл
def add_pending_request(chat_id, user_id):
    data = update_daily_limit()
    data['pending_requests'].append({'chat_id': chat_id, 'user_id': user_id})
    save_data(data)

# Удаление обработанной заявки
def remove_pending_request(chat_id, user_id):
    data = load_data()
    data['pending_requests'] = [
        req for req in data['pending_requests']
        if not (req['chat_id'] == chat_id and req['user_id'] == user_id)
    ]
    save_data(data)

# Увеличение счётчика заявок
def increment_request_count():
    data = load_data()
    data['count'] += 1
    save_data(data)
    return data['count']

# Обработчик заявок на вступление
@dp.chat_join_request()
async def handle_join_request(update: ChatJoinRequest):
    try:
        if update.chat.id not in CHAT_IDS:
            return

        # Сохраняем заявку в файл
        add_pending_request(update.chat.id, update.from_user.id)

        data = update_daily_limit()

        if data['count'] >= DAILY_LIMIT:
            print(f"Лимит заявок достигнут: {data['count']}")
            return

        # Одобряем заявку
        await bot.approve_chat_join_request(chat_id=update.chat.id, user_id=update.from_user.id)
        increment_request_count()
        remove_pending_request(update.chat.id, update.from_user.id)
        print(f"Заявка от {update.from_user.username} одобрена.")
    except Exception as e:
        print(f"Ошибка при обработке заявки: {e}")

# Обработка старых заявок при перезапуске
async def process_pending_requests():
    data = update_daily_limit()

    if data['count'] >= DAILY_LIMIT:
        print("Лимит уже достигнут. Пропускаем обработку старых заявок.")
        return

    for request in data['pending_requests']:
        try:
            if data['count'] < DAILY_LIMIT:
                await bot.approve_chat_join_request(chat_id=request['chat_id'], user_id=request['user_id'])
                increment_request_count()
                remove_pending_request(request['chat_id'], request['user_id'])
                print(f"Старая заявка от пользователя {request['user_id']} одобрена.")
            else:
                print("Лимит достигнут. Остановка обработки старых заявок.")
                return
        except Exception as e:
            print(f"Ошибка при обработке старой заявки: {e}")

# Основная функция
async def main():
    await process_pending_requests()  # Обрабатываем старые заявки при запуске
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("Бот запущен и готов к работе.")
    asyncio.run(main())
