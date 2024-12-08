import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup
import json

API_TOKEN = "8188712922:AAHyTWd6xgxOwEbYTS7oAlLNl-2_oLOleyQ"
CHAT_IDS = [-1002284058357, -1002248182741]  # Список ID всех групп
DAILY_LIMIT = 500
DATA_FILE = 'join_requests.json'
ADMIN_ID = 123456789  # Укажите ID администратора

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Функция для загрузки данных
def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {
            'count': 0,
            'last_reset': str(datetime.now().date()),
            'pending_requests': [],
            'settings': {
                'DEVSCHAT': {'accept_requests': False, 'limit': 0},
                'FILMS': {'accept_requests': True, 'limit': 0},
                'OKO': {'accept_requests': True, 'limit': 200}
            }
        }

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

# Функция для сброса лимита заявок, если новый день
def update_daily_limit():
    data = load_data()
    today = str(datetime.now().date())

    if data['last_reset'] != today:
        data['count'] = 0
        data['last_reset'] = today
        data['pending_requests'] = []  # Очищаем заявки, если старые уже обработаны
        save_data(data)
    return data

# Обработчик заявок на вступление
@dp.chat_join_request()
async def handle_join_request(update: ChatJoinRequest):
    try:
        if update.chat.id not in CHAT_IDS:
            return

        data = update_daily_limit()

        group_settings = data['settings'].get(str(update.chat.id), None)
        if not group_settings:
            return

        # Проверка настроек группы
        if not group_settings['accept_requests']:
            print(f"Заявки не принимаются в группу {update.chat.id}.")
            return

        # Если есть лимит, проверяем его
        if group_settings['limit'] > 0 and data['count'] >= group_settings['limit']:
            print(f"Лимит заявок для группы {update.chat.id} достигнут.")
            return

        # Сохраняем заявку в файл
        add_pending_request(update.chat.id, update.from_user.id)

        # Одобряем заявку
        await bot.approve_chat_join_request(chat_id=update.chat.id, user_id=update.from_user.id)
        increment_request_count()
        remove_pending_request(update.chat.id, update.from_user.id)
        print(f"Заявка от {update.from_user.username} одобрена.")
    except Exception as e:
        print(f"Ошибка при обработке заявки: {e}")

# Команда для панели управления
@dp.message_handler(commands=['settings'])
async def settings_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    keyboard = InlineKeyboardMarkup(row_width=1)
    # Кнопки для каждой группы
    keyboard.add(InlineKeyboardButton("DEVSCHAT", callback_data='devschat'))
    keyboard.add(InlineKeyboardButton("FILMS", callback_data='films'))
    keyboard.add(InlineKeyboardButton("OKO", callback_data='oko'))
    
    await message.answer("Выберите группу для настройки", reply_markup=keyboard)

# Обработчик кнопок настройки
@dp.callback_query_handler(text=["devschat", "films", "oko"])
async def settings_callback(call: types.CallbackQuery):
    data = load_data()
    group = call.data.upper()

    # Настройки группы
    settings = data['settings'][group]
    current_status = "Активированы" if settings['accept_requests'] else "Не активированы"
    limit = settings['limit'] if settings['limit'] > 0 else "Без ограничений"

    message = f"Группа: {group}\n"
    message += f"Прием заявок: {current_status}\n"
    message += f"Лимит заявок: {limit}\n\n"
    message += "Выберите действие:\n"
    message += "1. Включить/выключить прием заявок\n"
    message += "2. Изменить лимит заявок"

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("Изменить прием заявок", callback_data=f"toggle_{group}"))
    keyboard.add(InlineKeyboardButton("Изменить лимит", callback_data=f"limit_{group}"))

    await call.message.edit_text(message, reply_markup=keyboard)

# Обработчик изменения состояния приема заявок
@dp.callback_query_handler(lambda call: call.data.startswith("toggle_"))
async def toggle_accept_requests(call: types.CallbackQuery):
    group = call.data.split('_')[1].upper()
    data = load_data()
    current_status = data['settings'][group]['accept_requests']
    new_status = not current_status
    data['settings'][group]['accept_requests'] = new_status
    save_data(data)

    status = "включен" if new_status else "выключен"
    await call.message.edit_text(f"Прием заявок для {group} {status}.")

# Обработчик изменения лимита заявок
@dp.callback_query_handler(lambda call: call.data.startswith("limit_"))
async def set_limit(call: types.CallbackQuery):
    group = call.data.split('_')[1].upper()
    await call.message.edit_text(f"Введите новый лимит для {group} (0 для без ограничений):")
    await dp.message_handler(lambda message: message.text.isdigit())(handle_limit_set)

async def handle_limit_set(message: types.Message):
    if message.text.isdigit():
        limit = int(message.text)
        group = message.text.split(' ')[0]  # Получаем группу, передавшую запрос
        data = load_data()
        data['settings'][group]['limit'] = limit
        save_data(data)
        await message.answer(f"Лимит для {group} успешно обновлен на {limit}.")
    else:
        await message.answer("Пожалуйста, введите корректное число.")

# Основная функция
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("Бот запущен и готов к работе.")
    asyncio.run(main())
