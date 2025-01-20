import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
import json

API_TOKEN = "8188712922:AAHyTWd6xgxOwEbYTS7oAlLNl-2_oLOleyQ"
CHAT_IDS = [-1002284058357, -1002248182741]  # Список ID всех групп
DAILY_LIMIT = 500
DATA_FILE = 'join_requests.json'
ADMIN_ID = 7329088827  # Укажите ID администратора

bot = Bot(token=API_TOKEN)

# Создаем диспетчер
dp = Dispatcher()

# Создаем роутер
router = Router()

# Регистрируем роутер в диспетчере
dp.include_router(router)
REMOVING_GROUP = False
# Функция для загрузки данных
def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        print("Данные успешно загружены:", data)  # Логируем загруженные данные
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Ошибка при загрузке данных: {e}")  # Логируем ошибку
        data = {
            'count': 0,
            'last_reset': str(datetime.now().date()),
            'pending_requests': [],
            'settings': {}
        }
    return data


# Функция для сохранения данных
def save_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        print("Данные успешно сохранены:", data)  # Логируем сохраненные данные
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")  # Логируем ошибку


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
@router.chat_join_request()
async def handle_join_request(update: ChatJoinRequest):
    try:
        if update.chat.id not in CHAT_IDS:
            return

        data = update_daily_limit()

        group_settings = data['settings'].get(update.chat.id, None)
        if not group_settings:
            print(f"Нет настроек для группы: {update.chat.id}")
            return

        # Проверка настроек группы
        if not group_settings['accept_requests']:
            print(f"Заявки не принимаются в группе {update.chat.id}.")
            return

        # Если есть лимит, проверяем его
        if group_settings['limit'] > 0 and data['count'] >= group_settings['limit']:
            print(f"Лимит заявок для группы {update.chat.id} достигнут.")
            return

        # Одобряем заявку
        await bot.approve_chat_join_request(chat_id=update.chat.id, user_id=update.from_user.id)
        data['count'] += 1
        save_data(data)
        print(f"Заявка от {update.from_user.username} одобрена.")
    except Exception as e:
        print(f"Ошибка при обработке заявки: {e}")

# Команда для панели управления
@router.message(F.text.startswith('/settings'))
async def settings_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("У вас нет прав для использования этой команды.")
        return

    # Загружаем все группы из данных
    data = load_data()
    groups = data['settings'].keys()

    # Создаем кнопки для всех групп
    keyboard_buttons = [
        [InlineKeyboardButton(text=group, callback_data=f"settings_{group.lower()}")] for group in groups
    ]
    keyboard_buttons.append([InlineKeyboardButton(text="Добавить группу", callback_data='add_group')])
    keyboard_buttons.append([InlineKeyboardButton(text="Удалить группу", callback_data='remove_group')])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await message.answer("Выберите действие", reply_markup=keyboard)

# Обработчик для кнопки добавления группы
@router.callback_query(F.data == "add_group")
async def add_group_callback(call: CallbackQuery):
    await call.message.answer("Введите название группы и ID через запятую (например, MyGroup,-1001234567890):")

# Обработчик для добавления новой группы
@router.message(F.text)
async def add_group_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    if ',' in message.text:
        try:
            name, chat_id = map(str.strip, message.text.split(',', 1))
            chat_id = int(chat_id)

            data = load_data()
            data['settings'][name.upper()] = {'accept_requests': True, 'limit': 0}
            save_data(data)

            await message.answer(f"Группа {name} с ID {chat_id} добавлена.")
        except ValueError:
            await message.answer("Неправильный формат. Используйте: название группы, ID.")


# Обработчик для кнопки удаления группы
@router.callback_query(F.data == "remove_group")
async def remove_group_callback(call: CallbackQuery):
    global REMOVING_GROUP
    REMOVING_GROUP = True
    print("Запущен процесс удаления группы.")  # Логируем начало процесса удаления
    await call.message.answer("Введите название группы, которую нужно удалить:")

# Обработчик для удаления группы
@router.message(F.text)
async def handle_remove_group(message: Message):
    global REMOVING_GROUP

    # Логируем, что поступило сообщение
    print(f"Сообщение получено от {message.from_user.username}: {message.text}")

    if message.from_user.id != ADMIN_ID:
        return

    if REMOVING_GROUP:
        # Логируем, что флаг REMOVING_GROUP активен
        print(f"Флаг REMOVING_GROUP активен: {REMOVING_GROUP}")
        
        # Проверяем, был ли запущен процесс удаления
        data = load_data()
        group_name = message.text.strip().upper()

        # Логируем введенное название группы
        print(f"Попытка удалить группу: {group_name}")

        if group_name in data['settings']:
            del data['settings'][group_name]
            save_data(data)
            await message.answer(f"Группа {group_name} успешно удалена.")
            print(f"Группа {group_name} успешно удалена.")
        else:
            await message.answer(f"Группа {group_name} не найдена в настройках.")
            print(f"Группа {group_name} не найдена в настройках.")

        # Сбрасываем флаг после обработки
        REMOVING_GROUP = False
        print("Флаг REMOVING_GROUP сброшен.")
    else:
        print("Флаг REMOVING_GROUP не активен. Сообщение не обработано.")


# Обработчик для перехода в настройки группы
@router.callback_query(F.data.startswith("settings_"))
async def settings_callback(call: CallbackQuery):
    try:
        group_name = call.data.split('_', 1)[1].upper()
        data = load_data()

        group_settings = data['settings'].get(group_name, None)
        if not group_settings:
            await call.message.answer(f"Настройки для группы {group_name} не найдены.")
            return

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"Автоматически принимать заявки: {'Да' if group_settings['accept_requests'] else 'Нет'}", callback_data=f"accept_requests_{group_name}")],
                [InlineKeyboardButton(text=f"Лимит заявок: {group_settings['limit'] if group_settings['limit'] else 'Нет'}", callback_data=f"limit_{group_name}")],
                [InlineKeyboardButton(text="Назад", callback_data="settings")]
            ]
        )
        await call.message.answer(f"Настройки для группы {group_name}:", reply_markup=keyboard)

    except Exception as e:
        print(f"Ошибка при обработке настроек для группы: {e}")
        await call.answer("Произошла ошибка при обработке запроса.")

# Обработчик изменения настройки "Автоматически принимать заявки"
@router.callback_query(F.data.startswith("accept_requests_"))
async def toggle_accept_requests(call: CallbackQuery):
    group_name = call.data.split('_', 1)[1].upper()
    data = load_data()

    if group_name in data['settings']:
        data['settings'][group_name]['accept_requests'] = not data['settings'][group_name]['accept_requests']
        save_data(data)
        status = 'включено' if data['settings'][group_name]['accept_requests'] else 'выключено'
        await call.message.answer(f"Автоматическое принятие заявок для группы {group_name} {status}.")
    else:
        await call.message.answer(f"Группа {group_name} не найдена в настройках.")

# Обработчик изменения лимита заявок
@router.callback_query(F.data.startswith("limit_"))
async def change_limit(call: CallbackQuery):
    group_name = call.data.split('_', 1)[1].upper()
    data = load_data()

    if group_name in data['settings']:
        await call.message.answer(f"Введите новый лимит для группы {group_name} (0 — без ограничений):")

        # Ожидаем следующее сообщение с лимитом
        @router.message(F.text)
        async def set_limit(message: Message):
            if message.chat.id != call.message.chat.id or message.from_user.id != ADMIN_ID:
                return

            try:
                limit = int(message.text)
                if limit < 0:
                    await message.answer("Лимит не может быть отрицательным.")
                    return

                data['settings'][group_name]['limit'] = limit
                save_data(data)
                await message.answer(f"Лимит для группы {group_name} установлен на {limit}.")
            except ValueError:
                await message.answer("Пожалуйста, введите числовое значение.")
    else:
        await call.message.answer(f"Группа {group_name} не найдена в настройках.")

# Основная функция
async def main():
    print("Бот запущен и готов к работе.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
