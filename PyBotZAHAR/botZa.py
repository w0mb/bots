import asyncio
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from config import TOKEN
from datetime import datetime, timedelta

# Создаем экземпляр бота
bot = Bot(token=TOKEN)

# Создаем диспетчер
dp = Dispatcher()

# Создаем роутер
router = Router()

# Регистрируем роутер в диспетчере
dp.include_router(router)

# Создаем клавиатуру для действий (инлайн)
# action1_button = InlineKeyboardButton(text="Архив ссучек (месяц)", callback_data="action1")
action2_button = InlineKeyboardButton(text="Приватка (НАВСЕГДА)💥", callback_data="action2")
action_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[action2_button]]  # Инлайн-кнопки действий
)

accepting_requests = True

# Обработчик команды /start
@router.message(Command(commands=['start']))
async def start_handler(message: Message):
    await message.answer("💜 Приватка Premium ❤️\n\t\t👻Приветствует вас👻")
    image_path = "image.jpg"  # Укажите имя файла изображения
    photo = FSInputFile(image_path)
    caption = (
        "↘️ ❗️Наши правила❗️ ↙️\n\n"
        "• только эксклюзивный контент 🔥\n"
        "• полная анонимность 🔒\n"
        "• постоянные пополнения приватки ♻️\n\n"
        "• Резервный бот на случай бана приватки\n\n"
        "Более подробная информация о приватном канале в статье👇\n"
        
    )
    await message.answer_photo(photo, caption=caption)
    await message.answer("Выберите действие:", reply_markup=action_keyboard)

# Обработчик для "Действия 1"
@router.callback_query(lambda query: query.data == "action1")
async def action1_handler(query: types.CallbackQuery):
    await query.answer()
    new_text = (
        "Тариф: Приватка (навсегда)\n"
        "Стоимость: 600.00 RUB\n"
        "Доступ к:\n"
        "• 😈 Приватка Premium 👑\n\n"
        "Получите доступ:\n"
        "К видеоматериалам со скрытых камер 💦\n"
        "Видео с лицом без блюра 🍓\n"
        "Самый сочный материал,которого нигде нет💯\n\n"
    )
    await query.message.edit_text(new_text, reply_markup=None)

    # Добавляем кнопки "Оплатить" и "👈назад"
    pay_button = InlineKeyboardButton(text="💳 Оплатить", callback_data="pay_action1")
    back_button = InlineKeyboardButton(text="👈назад", callback_data="back_to_actions")
    back_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[pay_button], [back_button]]
    )
    await query.message.edit_reply_markup(reply_markup=back_keyboard)

async def auto_accept_requests():
    """
    Автоматически принимает все заявки на вступление в группу с заданным chat_id.
    :param chat_id: ID группы, где нужно обрабатывать заявки.
    """
    global accepting_requests
    chat_id = -1002028462189
    while accepting_requests:
        try:
            # Получаем новые заявки
            pending_requests = await bot.get_chat_join_requests(chat_id)
            
            # Проверяем наличие заявок
            if not pending_requests:
                print("Новых заявок нет.")
            else:
                for request in pending_requests:
                    user_id = request.from_user.id
                    await bot.approve_chat_join_request(chat_id, user_id)
                    print(f"Заявка от пользователя {user_id} успешно одобрена.")
                    
            # Задержка перед следующим опросом (в секундах)
            await asyncio.sleep(1)

        except TelegramAPIError as e:
            print(f"Ошибка при обработке заявок: {e}")
            await asyncio.sleep(30)  # Ожидаем 30 секунд при возник
            

            
async def monitor_terminal():
    """
    Мониторинг ввода пользователя в терминале.
    При вводе 'stop_accepting' завершает прием заявок.
    """
    global accepting_requests
    while True:
        user_input = await asyncio.get_event_loop().run_in_executor(None, input, "Введите команду: ")
        if user_input.strip().lower() == "stop_accepting":
            accepting_requests = False
            print("Прием заявок остановлен.")
            break

# Обработчик для кнопки "оплатить" в "Действие 1"
@router.callback_query(lambda query: query.data == "pay_action1")
async def pay_action1_handler(query: types.CallbackQuery):
    await query.answer()
    payment_text = "✅ Счёт на оплату сформирован. Доступы к закрытым сообществам будут открыты, как только вы оплатите его. Платите строго по реквизитам и ту сумму, которая была указана"
    await query.message.edit_text(payment_text)

    pay_button = InlineKeyboardButton(text="💳 Перейти к оплате", callback_data="go_to_payment")
    cancel_button = InlineKeyboardButton(text="🚫 Отмена", callback_data="back_to_actions")
    payment_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[pay_button], [cancel_button]]
    )
    await query.message.edit_reply_markup(reply_markup=payment_keyboard)

# Обработчик для кнопки "Перейти к оплате" в "Действие 1"
@router.callback_query(lambda query: query.data == "go_to_payment")
async def go_to_payment_handler(query: types.CallbackQuery):
    await query.answer()
    card_number = "💳 Ваш номер карты для оплаты: 2202205347906148\n\nКовалев Даниил Артемович(сбер)\n\n399.00 рублей\n\nПожалуйста, нажмите 'Оплатил', когда завершите оплату и ожидайте доступ."
    
    # Создаем клавиатуру с кнопкой "Оплатил" и "Отмена"
    paid_button = InlineKeyboardButton(text="💸 Оплатил", callback_data="payment_done")
    cancel_button = InlineKeyboardButton(text="🚫 Отмена", callback_data="back_to_actions")
    payment_keyboard = InlineKeyboardMarkup(inline_keyboard=[[paid_button], [cancel_button]])

    # Отправляем отредактированное сообщение с номером карты и кнопками
    await query.message.edit_text(card_number, reply_markup=payment_keyboard)
# Обработчик для кнопки "Оплатил"
@router.callback_query(lambda query: query.data == "payment_done")
async def payment_done_handler(query: types.CallbackQuery):
    await query.answer()

    # Получаем информацию о пользователе
    user_id = query.from_user.id
    username = query.from_user.username
    first_name = query.from_user.first_name
    last_name = query.from_user.last_name

    # Вычисляем дату окончания подписки через месяц
    end_date = datetime.now() + timedelta(days=30)
    end_date_str = end_date.strftime("%Y-%m-%d")

    # Записываем информацию о подписке в файл
    with open("subscriptions.txt", "a") as file:
        file.write(f"{username}:{end_date_str}\n")

    message_to_send = (
        f"ПРИВАТКА\n"
        f"Пользователь нажал оплату:\n"
        f"ID: {user_id}\n"
        f"Имя: {first_name} {last_name}\n"
        f"Username: @{username}"
        f"ПРИВАТКА\n"
    )
    approve_button = InlineKeyboardButton(text="Разрешить доступ", callback_data=f"approve_access:{user_id}")
    try:
        await bot.send_message(chat_id=-1002498160000, text=message_to_send, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[approve_button]]))
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

    await query.message.answer("Спасибо за оплату! Доступы к закрытым сообществам будут открыты в ближайшее время.")
    
# Обработчик для кнопки "разрешить доступ"
@router.callback_query(lambda query: query.data.startswith("approve_access:"))
async def approve_access_handler(query: types.CallbackQuery):
    await query.answer()
    user_id = int(query.data.split(":")[1])
    access_link = "https://t.me/+CoJCYExq11M4ZTUy"
    try:
        await bot.send_message(chat_id=user_id, text=f"🎉 Доступ к контенту получен! Вот ваша ссылка: {access_link}")
        await query.message.answer("ПРИВАТКА Доступ предоставлен пользователю. ПРИВАТКА")
    except Exception as e:
        print(f"Ошибка при отправке ссылки пользователю: {e}")
        await query.message.answer("Не удалось отправить ссылку. Попробуйте еще раз.")




# Обработчик для кнопки "назад"
@router.callback_query(lambda query: query.data == "back_to_actions")
async def back_to_actions_handler(query: types.CallbackQuery):
    await query.answer()  # Подтверждаем нажатие кнопки
    await query.message.edit_text("Выберите действие:", reply_markup=action_keyboard)
    
async def remove_expired_users():
    group_id = -1002498160000
    updated_subscribers = []
    current_date = datetime.date.today()
    
    # Открываем файл с подписками и считываем данные
    with open("subscribers.txt", "r") as file:
        for line in file:
            username, expiration_date_str = line.strip().split(":")
            expiration_date = datetime.datetime.strptime(expiration_date_str, "%Y-%m-%d").date()
            
            # Проверяем, истекла ли дата подписки
            if expiration_date < current_date:
                # Если подписка истекла, удаляем пользователя из группы
                try:
                    user_id = await bot.get_chat_member(group_id, username)
                    await bot.kick_chat_member(group_id, user_id.user.id)
                    print(f"Пользователь @{username} удалён из группы.")
                except Exception as e:
                    print(f"Не удалось удалить пользователя @{username}: {e}")
            else:
                # Сохраняем активные подписки
                updated_subscribers.append(f"{username}:{expiration_date_str}")
    
    # Перезаписываем файл только с активными подписками
    with open("subscribers.txt", "w") as file:
        for line in updated_subscribers:
            file.write(line + "\n")
            
# Обработчик для "Действия 2"
@router.callback_query(lambda query: query.data == "action2")
async def action2_handler(query: types.CallbackQuery):
    await query.answer()
    new_text = (
        "Тариф: Приватка (навсегда)\n"
        "Стоимость: 600.00 RUB\n"
        "Доступ к:\n"
        "•Приватка Premium 👑\n\n"
        "Получите доступ:\n"
        "К видеоматериалам со скрытых камер 💦\n"
        "Видео с лицом без блюра 🍓\n"
        "Самый сочный материал,которого нигде нет💯\n\n"
    
    )
    await query.message.edit_text(new_text, reply_markup=None)

    # Добавляем кнопки "Оплатить" и "👈назад"
    pay_button = InlineKeyboardButton(text="💳 Оплатить", callback_data="pay_action2")
    back_button = InlineKeyboardButton(text="👈назад", callback_data="back_to_actions")
    back_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[pay_button], [back_button]]
    )
    await query.message.edit_reply_markup(reply_markup=back_keyboard)

# Обработчик для кнопки "оплатить" в "Действие 2"
@router.callback_query(lambda query: query.data == "pay_action2")
async def pay_action2_handler(query: types.CallbackQuery):
    await query.answer()
    payment_text = "✅ Счёт на оплату сформирован. Доступы к закрытым сообществам будут открыты, как только вы оплатите его. Платите строго по реквизитам и ту сумму, которая была указана"
    await query.message.edit_text(payment_text)

    pay_button = InlineKeyboardButton(text="💳 Перейти к оплате", callback_data="go_to_payment2")
    cancel_button = InlineKeyboardButton(text="🚫 Отмена", callback_data="back_to_actions")
    payment_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[pay_button], [cancel_button]]
    )
    await query.message.edit_reply_markup(reply_markup=payment_keyboard)

# Обработчик для кнопки "Перейти к оплате" в "Действие 2"
@router.callback_query(lambda query: query.data == "go_to_payment2")
async def go_to_payment2_handler(query: types.CallbackQuery):
    await query.answer()
    card_number = "💳 Ваш номер карты для оплаты: 2202205347906148\n\nКовалев Даниил Артемович(сбер)\n\n600.00 рублей\n\nПожалуйста, нажмите 'Оплатил', когда завершите оплату и ожидайте доступ."

    # Создаем клавиатуру с кнопкой "Оплатил" и "Отмена"
    paid_button = InlineKeyboardButton(text="💸 Оплатил", callback_data="payment_done2")
    cancel_button = InlineKeyboardButton(text="🚫 Отмена", callback_data="back_to_actions")
    payment_keyboard = InlineKeyboardMarkup(inline_keyboard=[[paid_button], [cancel_button]])

    # Отправляем отредактированное сообщение с номером карты и кнопками
    await query.message.edit_text(card_number, reply_markup=payment_keyboard)

# Обработчик для кнопки "Оплатил" в "Действие 2"
@router.callback_query(lambda query: query.data == "payment_done2")
async def payment_done2_handler(query: types.CallbackQuery):
    await query.answer()

    # Получаем информацию о пользователе
    user_id = query.from_user.id
    username = query.from_user.username
    first_name = query.from_user.first_name
    last_name = query.from_user.last_name

    # Бессрочная подписка
    end_date_str = "навсегда"

    # Записываем информацию о подписке в файл
    with open("subscriptions.txt", "a") as file:
        file.write(f"{username}:{end_date_str}\n")

    message_to_send = (
        f"ПРИВАТКА\n"
        f"Пользователь нажал оплату:\n"
        f"ID: {user_id}\n"
        f"Имя: {first_name} {last_name}\n"
        f"Username: @{username}"
        f"\nПРИВАТКА\n"
    )
    approve_button = InlineKeyboardButton(text="Разрешить доступ", callback_data=f"approve_access:{user_id}")
    try:
        await bot.send_message(chat_id=-1002498160000, text=message_to_send, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[approve_button]]))
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

    await query.message.answer("Спасибо за оплату! Доступы к закрытым сообществам будут открыты в ближайшее время.\n\nДля более быстрой проверки платежа, отправьте скриншот оплаты")

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 МБ в байтах

@router.message(F.photo | F.document)
async def process_media(message: Message ):
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
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

        # Получаем информацию о пользователе
        username = message.from_user.username or message.from_user.first_name or f"ID: {message.from_user.id}"
        caption = f"ПРИВАТКА Отправлено пользователем: @{username}" if message.from_user.username else f"ПРИВАТКА Отправлено пользователем: {first_name} {last_name}"

        # Отправляем файл с подписью
        if message.photo:
            # Отправляем фото с подписью
            await bot.send_photo(chat_id='-1002498160000', photo=file.file_id, caption=caption)
        elif message.document:
            # Отправляем документ с подписью
            await bot.send_document(chat_id='-1002498160000', document=file.file_id, caption=caption)
    else:
        await message.answer("Отправленный файл не поддерживается.")
            
if __name__ == '__main__':
    print("бот стартанул")

    # Создаем новый цикл событий
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Создаём задачи для всех функций
    tasks = [
        loop.create_task(dp.start_polling(bot)),
        loop.create_task(auto_accept_requests()),
        loop.create_task(monitor_terminal())
    ]

    loop.run_until_complete(asyncio.wait(tasks))

