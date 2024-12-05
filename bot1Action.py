import asyncio
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from БотОплат.config import TOKEN
from datetime import datetime, timedelta

# Создаем экземпляр бота
bot = Bot(token=TOKEN)

# Создаем диспетчер
dp = Dispatcher()

# Создаем роутер
router = Router()

# Регистрируем роутер в диспетчере
dp.include_router(router)

# Создаем клавиатуру для действия
action_button = InlineKeyboardButton(text="Архив ссучек (499.00 🇷🇺RUB)", callback_data="action")
action_keyboard = InlineKeyboardMarkup(inline_keyboard=[[action_button]])

# Обработчик команды /start
@router.message(Command(commands=['start']))
async def start_handler(message: Message):
    await message.answer("💜 Слитые ссучки Premium ❤️\n\t\t👻Приветствует вас👻")
    image_path = "image.jpg"  # Укажите имя файла изображения
    photo = FSInputFile(image_path)
    caption = (
        "↘️ ❗️Наши правила❗️ ↙️\n\n"
        "• только эксклюзивный контент 🔥\n"
        "• полная анонимность 🔒\n"
        "• постоянные пополнения архива ♻️\n\n"
        "Более подробная информация о приватном канале в статье👇\n"
        "https://telegra.ph/Privatnyj-kanal-09-11"
    )
    await message.answer_photo(photo, caption=caption)
    await message.answer("Выберите действие:", reply_markup=action_keyboard)

# Обработчик для действия (тариф)
@router.callback_query(lambda query: query.data == "action")
async def action_handler(query: types.CallbackQuery):
    await query.answer()
    new_text = (
        "Тариф: Архив ссучек\nСтоимость: 499.00 🇷🇺RUB\n"
        "Вы получите доступ к следующим ресурсам:\n\n"
        "• 😈Слитые ссучки Premium👑 (канал)\n\n"
        "👇ПРИ ПОКУПКЕ ВЫ ПОЛУЧАЕТЕ👇\n\n"
        "🗂 Более 25TB материала без цензуры\n"
        "👉 [ Фото | Видео ]\n\n"
        "📱 Контактные данные слитых знаменитостей\n"
        "👉 [ ВК | Инстаграм | Номера телефонов ]\n\n"
        "🙅‍♂️ Весь секретный контент, полученный от бывших парней этих девушек"
    )
    # Клавиатура с кнопками "Оплатить" и "Отмена"
    pay_button = InlineKeyboardButton(text="💳 Оплатить", callback_data="pay_action")
    cancel_button = InlineKeyboardButton(text="🚫 Отмена", callback_data="cancel")
    payment_keyboard = InlineKeyboardMarkup(inline_keyboard=[[pay_button], [cancel_button]])
    await query.message.edit_text(new_text, reply_markup=payment_keyboard)

# Обработчик для кнопки "Оплатить"
@router.callback_query(lambda query: query.data == "pay_action")
async def pay_action_handler(query: types.CallbackQuery):
    await query.answer()
    payment_text = "✅ Счёт на оплату сформирован. Доступы к закрытым сообществам будут открыты, как только вы оплатите его."
    # Клавиатура с кнопками "Оплатил" и "Отмена"
    paid_button = InlineKeyboardButton(text="💸 Оплатил", callback_data="payment_done")
    cancel_button = InlineKeyboardButton(text="🚫 Отмена", callback_data="cancel")
    await query.message.edit_text(payment_text, reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[[paid_button], [cancel_button]]
    ))

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
        f"Пользователь нажал оплату:\n"
        f"ID: {user_id}\n"
        f"Имя: {first_name} {last_name}\n"
        f"Username: @{username}"
    )
    approve_button = InlineKeyboardButton(text="Разрешить доступ", callback_data=f"approve_access:{user_id}")
    try:
        await bot.send_message(chat_id=-1002460014339, text=message_to_send, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[approve_button]]))
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

    await query.message.answer("Спасибо за оплату! Доступы к закрытым сообществам будут открыты в ближайшее время.")

# Обработчик для кнопки "разрешить доступ"
@router.callback_query(lambda query: query.data.startswith("approve_access:"))
async def approve_access_handler(query: types.CallbackQuery):
    await query.answer()
    user_id = int(query.data.split(":")[1])
    access_link = "https://t.me/slituesuchu"
    try:
        await bot.send_message(chat_id=user_id, text=f"🎉 Доступ к контенту получен! Вот ваша ссылка: {access_link}")
        await query.message.answer("Доступ предоставлен пользователю.")
    except Exception as e:
        print(f"Ошибка при отправке ссылки пользователю: {e}")
        await query.message.answer("Не удалось отправить ссылку. Попробуйте еще раз.")

# Обработчик для кнопки "Отмена" — возвращение в предыдущее меню
@router.callback_query(lambda query: query.data == "cancel")
async def cancel_handler(query: types.CallbackQuery):
    await query.answer()
    await query.message.edit_text("Выберите действие:", reply_markup=action_keyboard)

if __name__ == '__main__':
    print("бот стартанул")
    asyncio.run(dp.start_polling(bot))
