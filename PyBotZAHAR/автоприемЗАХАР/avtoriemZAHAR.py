import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatJoinRequest
import json

API_TOKEN = "7847004083:AAHcqJ4tDCjuHRPKzmWWYCCKhfTStoyI7uU"
CHAT_ID = -1002284058357
DAILY_LIMIT = 500
ADMIN_IDS = [7329088827, 2144528028]  # ID админа, которому будут приходить сообщения

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

DATA_FILE = 'join_requests.json'

# Проверяем, является ли пользователь администратором
def is_admin(user_id):
    return user_id in ADMIN_IDS

# Функция для загрузки данных
def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {'count': 0, 'last_reset': str(datetime.now().date()), 'approved_users': []}
    if 'approved_users' not in data:
        data['approved_users'] = []
    return data

# Функция для сохранения данных
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)
# Функция обновления счетчика и добавления пользователя в список одобренных
def update_request_count(user):
    data = load_data()
    today = str(datetime.now().date())

    # Сброс счётчика, если наступил новый день
    if data['last_reset'] != today:
        data = {'count': 0, 'last_reset': today, 'approved_users': []}

    data['count'] += 1
    # Добавляем username и id пользователя в список одобренных
    data['approved_users'].append({'username': user.username, 'id': user.id})
    save_data(data)
    return data['count']

# Пример использования функции проверки
@dp.message(F.text == "/start")
async def start_command_handler(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет прав для выполнения этой команды.")
        return

    # Код для отправки инлайн-кнопок только администраторам
    count_button = InlineKeyboardButton(text="Количество одобренных заявок", callback_data="show_count")
    usernames_button = InlineKeyboardButton(text="Список одобренных пользователей", callback_data="show_usernames")
    other_info_button = InlineKeyboardButton(text="Другая информация", callback_data="show_other_info")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[count_button], [usernames_button], [other_info_button]])
    
    await message.answer("Выберите действие:", reply_markup=keyboard)

@dp.callback_query(lambda query: query.data == "show_count")
async def show_count_handler(query: types.CallbackQuery):
    data = load_data()
    await query.message.answer(f"Одобрено заявок за сегодня: {data['count']}")
    await query.answer()

@dp.callback_query(lambda query: query.data == "show_usernames")
async def show_users_handler(query: types.CallbackQuery):
    data = load_data()
    # Корректно формируем список, если approved_users содержит объекты с username и id
    users_list = "\n".join([f"@{user['username']} (ID: {user['id']})" for user in data['approved_users']])
    await query.message.answer(f"Список одобренных пользователей:\n{users_list}")
    await query.answer()

@dp.callback_query(lambda query: query.data == "show_info")
async def show_info_handler(query: types.CallbackQuery):
    # Выводим дополнительную информацию
    await query.message.answer("Дополнительная информация будет здесь.")
    await query.answer()

@dp.chat_join_request(F.chat.id == CHAT_ID)
async def auto_approve_join_request(update: ChatJoinRequest, bot: Bot):
    try:
        current_count = update_request_count(update.from_user)

        # Проверяем лимит
        if current_count > DAILY_LIMIT:
            print(f"Лимит заявок достигнут: {current_count}")
            return

        await bot.approve_chat_join_request(chat_id=update.chat.id, user_id=update.from_user.id)
        print(f"Заявка от {update.from_user.username} одобрена. Текущее количество: {current_count}")
    except Exception as e:
        print(f"Ошибка при одобрении заявки: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("автоприем захара старт")
    asyncio.run(main())