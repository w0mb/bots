import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ChatJoinRequest, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.exceptions import TelegramAPIError

from config import TOKEN, CHAT_ID_APTEKA, CHAT_ID_DAVALKI, CHAT_ID_FILMS, CHAT_ID_CHANNEL2
from config import SECOND_TOKEN, CHAT_ID_CRYPTONEWS, CHAT_ID_PARABAKSOW
bot = Bot(token=TOKEN)
dp = Dispatcher()


bot2 = Bot(token=SECOND_TOKEN)
dp2 = Dispatcher()

# Инлайн-клавиатура с кнопкой "Подписался"
keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="ФИЛЬМЫ НА ВЕЧЕР", url="https://t.me/+wcGF5axatGY1MTEy")],
    [InlineKeyboardButton(text="Вестник", url="https://t.me/+6V7zpt30WdQzYjVi")],
    [InlineKeyboardButton(text="Перейти в канал", url="https://t.me/+tAFwdstcfzk0NWFl")],
    [InlineKeyboardButton(text="Подписался", callback_data="check_subscription")],
])

invite_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Перейти в канал", url=f"https://t.me/+tAFwdstcfzk0NWFl")]
])

# Инлайн-клавиатура с кнопкой "Подписался" и прямой ссылкой на канал CHAT_ID_CRYPTONEWS
keyboard2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Пара Баксов", url="https://t.me/+kpUif5DNlq85MTcy")],
    [InlineKeyboardButton(text="ФИЛЬМЫ НА ВЕЧЕР", url="https://t.me/+wcGF5axatGY1MTEy")],
    [InlineKeyboardButton(text="Перейти в канал CryptoNews", url="https://t.me/+NgOFBChKmcVhYzEy")],
    [InlineKeyboardButton(text="Подписался", callback_data="check_subscription_2")]
])



async def check_user_membership(user_id):
    try:
        # Проверяем наличие пользователя в обоих каналах
        is_member_in_channel_1 = await bot.get_chat_member(chat_id=CHAT_ID_FILMS, user_id=user_id)
        is_member_in_channel_2 = await bot.get_chat_member(chat_id=CHAT_ID_CHANNEL2, user_id=user_id)

        return is_member_in_channel_1.status != "left" and is_member_in_channel_2.status != "left"
    except exceptions.BotBlocked:
        print(f"Бот заблокирован пользователем {user_id}.")
    except exceptions.ChatAdminRequired:
        print(f"У бота нет прав администратора в чате.")
    except exceptions.UserAlreadyParticipant:
        print(f"Пользователь {user_id} уже в канале.")
    except TelegramAPIError as e:
        print(f"Произошла ошибка Telegram API: {e}")
        return False

@dp.chat_join_request(F.chat.id == CHAT_ID_DAVALKI)
async def send_subscription_request(update: ChatJoinRequest):
    user_id = update.from_user.id
    try:
        await bot.send_message(
            user_id,
            "Здравствуйте! Чтобы вступить в канал, подпишитесь на следующие каналы, затем нажмите 'Подписался':",
            reply_markup=keyboard
        )
    except TelegramAPIError as e:
        print(f"Ошибка при отправке сообщения: {e}")

@dp.callback_query(F.data == "check_subscription")
async def verify_subscription(callback: CallbackQuery):
    user_id = callback.from_user.id
    try:
        # Проверяем подписку на каналы
        if await check_user_membership(user_id):
            # Одобряем заявку в канал
            await bot.approve_chat_join_request(chat_id=CHAT_ID_DAVALKI, user_id=user_id)
            await callback.message.answer("Спасибо за подписку! Ваша заявка одобрена.")

            # Отправляем сообщение-приглашение в основной чат канала
            invite_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Перейти в канал", url=f"https://t.me/+n7OZ1AP4xdxmM2Ey")]
            ])
            await bot.send_message(user_id, "Добро пожаловать! Присоединяйтесь к обсуждению в нашем канале:", reply_markup=invite_keyboard)
            print(f"Заявка от {user_id} одобрена и приглашение отправлено")
        else:
            await callback.answer("Пожалуйста, убедитесь, что вы подписаны на оба канала.", show_alert=True)
    except TelegramAPIError as e:
        if "USER_ALREADY_PARTICIPANT" in str(e):
            # Если пользователь уже участник, отправляем сообщение с приглашением
            invite_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Перейти в канал", url=f"https://t.me/+n7OZ1AP4xdxmM2Ey")]
            ])
            await bot.send_message(user_id, "Вы уже подписаны на оба из каналов. Вы можете перейти в канал:", reply_markup=invite_keyboard)
            print(f"Пользователь {user_id} уже участник канала, отправлено приглашение.")
        else:
            print(f"Ошибка при проверке подписки или одобрении заявки: {e}")



# Функция проверки подписки для второго бота
async def check_user_membership2(user_id):
    try:
        is_member_in_channel_1 = await bot2.get_chat_member(chat_id=CHAT_ID_PARABAKSOW, user_id=user_id)
        is_member_in_channel_2 = await bot2.get_chat_member(chat_id=CHAT_ID_FILMS, user_id=user_id)
        return is_member_in_channel_1.status != "left" and is_member_in_channel_2.status != "left"
    except TelegramAPIError as e:
        print(f"Ошибка проверки подписки (бот 2): {e}")
        return False


@dp2.chat_join_request(F.chat.id == CHAT_ID_CRYPTONEWS)
async def send_subscription_request_2(update: ChatJoinRequest):
    user_id = update.from_user.id
    await bot2.send_message(
        user_id,
        "Подпишитесь на каналы и нажмите 'Подписался':",
        reply_markup=keyboard2
    )

@dp2.callback_query(F.data == "check_subscription_2")
async def verify_subscription_2(callback: CallbackQuery):
    user_id = callback.from_user.id

    # Определяем invite_keyboard2 заранее для использования в любом блоке кода
    invite_keyboard2 = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Перейти в канал", url="https://t.me/+NgOFBChKmcVhYzEy")]
    ])

    try:
        # Проверяем, подписан ли пользователь на нужные каналы через check_user_membership2
        if await check_user_membership2(user_id):
            # Одобряем заявку на вступление в канал и отправляем приветственное сообщение
            await bot2.approve_chat_join_request(chat_id=CHAT_ID_CRYPTONEWS, user_id=user_id)
            await callback.message.answer("Спасибо за подписку! Ваша заявка одобрена.")
            
            # Отправляем пользователю приглашение с переходом в основной канал
            await bot2.send_message(user_id, "Добро пожаловать! Присоединяйтесь к обсуждению в нашем канале:", reply_markup=invite_keyboard2)
            print(f"Заявка от {user_id} одобрена и приглашение отправлено")
        else:
            # Сообщаем пользователю, если он еще не подписан на оба канала
            await callback.answer("Пожалуйста, убедитесь, что вы подписаны на оба канала.", show_alert=True)
    except TelegramAPIError as e:
        # Обрабатываем случай, когда пользователь уже является участником канала
        if "USER_ALREADY_PARTICIPANT" in str(e):
            await bot2.send_message(user_id, "Вы уже подписаны на оба канала. Вы можете перейти в канал:", reply_markup=invite_keyboard2)
            print(f"Пользователь {user_id} уже участник канала, отправлено приглашение.")
        else:
            # Обработка прочих ошибок API
            print(f"Ошибка при проверке подписки или одобрении заявки: {e}")




async def main():
        await asyncio.gather(
        dp.start_polling(bot),
        dp2.start_polling(bot2)
    )

if __name__ == "__main__":
    print("боты трафика стартанул")
    asyncio.run(main())
