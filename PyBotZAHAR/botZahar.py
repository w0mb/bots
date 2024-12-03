import asyncio
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from datetime import datetime, timedelta
from config import TOKEN

# Создаем экземпляр бота
bot = Bot(token=TOKEN)

# Создаем диспетчер и роутер
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Кнопка для "Приватка (НАВСЕГДА)"
action_button = InlineKeyboardButton(text="Приватка(НАВСЕГДА)💥", callback_data="action")
action_keyboard = InlineKeyboardMarkup(inline_keyboard=[[action_button]])

accepting_requests = True

@router.message(Command(commands=['start']))
async def start_handler(message: Message):
    await message.answer("💜 Приватка Premium ❤️\n\t\t👻Приветствует вас👻")
    photo = FSInputFile("image.jpg")  # Укажите имя файла изображения
    await message.answer_photo(photo, caption=(
        "↘️ ❗️Наши правила❗️ ↙️\n\n"
        "• Постоянное пополнение приватки 🔥\n"
        "• Полная анонимность 🔒\n"
        "• Резервный бот на случай бана приватки ♻️\n\n"
        "Подробная информация в статье:\n"
        "https://telegra.ph/VHOD-V-VIP-ARHIV-10-31"
    ))
    await message.answer("Выберите действие:", reply_markup=action_keyboard)

@router.callback_query(lambda query: query.data == "action")
async def action_handler(query: types.CallbackQuery):
    await query.answer()
    new_text = (
        "Тариф: Приватка (навсегда)\n"
        "Стоимость: 1600.00 RUB\n"
        "Доступ к:\n"
        "• 😈 Приватка Premium 👑\n\n"
        "Получите:\n"
        "🗂 25TB материала без цензуры\n"
        "📱 Контакты слитых знаменитостей\n\n"
    )
    await query.message.edit_text(new_text, reply_markup=None)

    pay_button = InlineKeyboardButton(text="💳 Оплатить", callback_data="pay_action")
    back_button = InlineKeyboardButton(text="👈назад", callback_data="back_to_actions")
    await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup([[pay_button], [back_button]]))

@router.callback_query(lambda query: query.data == "pay_action")
async def pay_action_handler(query: types.CallbackQuery):
    await query.answer()
    await query.message.edit_text(
        "✅ Счёт на оплату сформирован. Оплатите по реквизитам:\n\n"
        "💳 Карта: 2202205347906148\n"
        "Ковалев Даниил Артемович (Сбер)\n"
        "Сумма: 1600.00 RUB"
    )
    paid_button = InlineKeyboardButton(text="💸 Оплатил", callback_data="payment_done")
    cancel_button = InlineKeyboardButton(text="🚫 Отмена", callback_data="back_to_actions")
    await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup([[paid_button], [cancel_button]]))

@router.callback_query(lambda query: query.data == "payment_done")
async def payment_done_handler(query: types.CallbackQuery):
    await query.answer()
    user_id = query.from_user.id
    end_date_str = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    with open("subscriptions.txt", "a") as file:
        file.write(f"{query.from_user.username}:{end_date_str}\n")

    await bot.send_message(
        chat_id=-1002498160000, 
        text=f"Оплата подтверждена:\nID: {user_id}\nUsername: @{query.from_user.username}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Разрешить доступ", callback_data=f"approve_access:{user_id}")]])
    )
    await query.message.answer("Спасибо за оплату! Ожидайте одобрения доступа.")

@router.callback_query(lambda query: query.data.startswith("approve_access:"))
async def approve_access_handler(query: types.CallbackQuery):
    await query.answer()
    user_id = int(query.data.split(":")[1])
    await bot.send_message(chat_id=user_id, text="🎉 Доступ получен! Ссылка: https://t.me/+CoJCYExq11M4ZTUy")
    await query.message.answer("Доступ предоставлен.")

@router.callback_query(lambda query: query.data == "back_to_actions")
async def back_to_actions_handler(query: types.CallbackQuery):
    await query.answer()
    await query.message.edit_text("Выберите действие:", reply_markup=action_keyboard)

async def remove_expired_users():
    group_id = -1002498160000
    current_date = datetime.today().date()
    with open("subscriptions.txt", "r") as file:
        subscriptions = [line.strip().split(":") for line in file]

    with open("subscriptions.txt", "w") as file:
        for username, expiration_date_str in subscriptions:
            expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%d").date()
            if expiration_date < current_date:
                try:
                    await bot.kick_chat_member(group_id, username)
                except Exception as e:
                    print(f"Не удалось удалить @{username}: {e}")
            else:
                file.write(f"{username}:{expiration_date_str}\n")
            
# Обработчик для "Действия 2"
# @router.callback_query(lambda query: query.data == "action2")
# async def action2_handler(query: types.CallbackQuery):
#     await query.answer()
#     new_text = (
#         "Тариф: Архив ссучек (НАВСЕГДА)\n"
#         "Стоимость: 999.00 🇷🇺RUB\n"
#         "Срок действия: бессрочный доступ\n\n"
#         "Вы получите доступ к следующим ресурсам:\n"
#         "• 😈Слитые ссучки Premium👑 (канал)\n\n"
#         "👇ПРИ ПОКУПКЕ ВЫ ПОЛУЧАЕТЕ👇\n\n"
#         "🗂 Более 25TB материала без цензуры\n"
#         "👉 [ Фото | Видео ]\n\n"
#         "📱 Контактные данные слитых знаменитостей\n"
#         "👉 [ ВК | Инстаграм | Номера телефонов ]\n\n"
#         "🙅‍♂️ Весь секретный контент, полученный от бывших парней этих девушек"
#     )
#     await query.message.edit_text(new_text, reply_markup=None)

#     # Добавляем кнопки "Оплатить" и "👈назад"
#     pay_button = InlineKeyboardButton(text="💳 Оплатить", callback_data="pay_action2")
#     back_button = InlineKeyboardButton(text="👈назад", callback_data="back_to_actions")
#     back_keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[[pay_button], [back_button]]
#     )
#     await query.message.edit_reply_markup(reply_markup=back_keyboard)

# # Обработчик для кнопки "оплатить" в "Действие 2"
# @router.callback_query(lambda query: query.data == "pay_action2")
# async def pay_action2_handler(query: types.CallbackQuery):
#     await query.answer()
#     payment_text = "✅ Счёт на оплату сформирован. Доступы к закрытым сообществам будут открыты, как только вы оплатите его. Платите строго по реквизитам и ту сумму, которая была указана"
#     await query.message.edit_text(payment_text)

#     pay_button = InlineKeyboardButton(text="💳 Перейти к оплате", callback_data="go_to_payment2")
#     cancel_button = InlineKeyboardButton(text="🚫 Отмена", callback_data="back_to_actions")
#     payment_keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[[pay_button], [cancel_button]]
#     )
#     await query.message.edit_reply_markup(reply_markup=payment_keyboard)

# # Обработчик для кнопки "Перейти к оплате" в "Действие 2"
# @router.callback_query(lambda query: query.data == "go_to_payment2")
# async def go_to_payment2_handler(query: types.CallbackQuery):
#     await query.answer()
#     card_number = "💳 Ваш номер карты для оплаты: 2202205347906148\n\nКовалев Даниил Артемович(сбер)\n\n999.00 рублей\n\nПожалуйста, нажмите 'Оплатил', когда завершите оплату и ожидайте доступ."

#     # Создаем клавиатуру с кнопкой "Оплатил" и "Отмена"
#     paid_button = InlineKeyboardButton(text="💸 Оплатил", callback_data="payment_done2")
#     cancel_button = InlineKeyboardButton(text="🚫 Отмена", callback_data="back_to_actions")
#     payment_keyboard = InlineKeyboardMarkup(inline_keyboard=[[paid_button], [cancel_button]])

#     # Отправляем отредактированное сообщение с номером карты и кнопками
#     await query.message.edit_text(card_number, reply_markup=payment_keyboard)

# # Обработчик для кнопки "Оплатил" в "Действие 2"
# @router.callback_query(lambda query: query.data == "payment_done2")
# async def payment_done2_handler(query: types.CallbackQuery):
#     await query.answer()

#     # Получаем информацию о пользователе
#     user_id = query.from_user.id
#     username = query.from_user.username
#     first_name = query.from_user.first_name
#     last_name = query.from_user.last_name

#     # Бессрочная подписка
#     end_date_str = "навсегда"

#     # Записываем информацию о подписке в файл
#     with open("subscriptions.txt", "a") as file:
#         file.write(f"{username}:{end_date_str}\n")

#     message_to_send = (
#         f"Пользователь нажал оплату:\n"
#         f"ID: {user_id}\n"
#         f"Имя: {first_name} {last_name}\n"
#         f"Username: @{username}"
#     )
#     approve_button = InlineKeyboardButton(text="Разрешить доступ", callback_data=f"approve_access:{user_id}")
#     try:
#         await bot.send_message(chat_id=-1002498160000, text=message_to_send, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[approve_button]]))
#     except Exception as e:
#         print(f"Ошибка при отправке сообщения: {e}")

#     await query.message.answer("Спасибо за оплату! Доступы к закрытым сообществам будут открыты в ближайшее время.")
                    
if __name__ == '__main__':
    print("бот стартанул")

    # Создаем новый цикл событий
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Создаём задачи для всех функций
    tasks = [
        loop.create_task(dp.start_polling(bot)),
        # loop.create_task(auto_accept_requests()),
        # loop.create_task(monitor_terminal())
    ]

    loop.run_until_complete(asyncio.wait(tasks))




