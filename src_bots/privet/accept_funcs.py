import asyncio

from aiogram import Bot, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from telebot.types import ChatJoinRequest

from inline_kb import Keyboard
from utils import get_strings_from_file
from captionTexts import text1, text_send2


from utils import save_string_to_file

channel_ids_filename = "chaneel_ids.txt"
join_request_data = {}
keyboards = {}



async def func_confirm_request(callback: CallbackQuery):
    """Обработка нажатия кнопки 'Подтвердить'"""
    bot = callback.bot
    user_id = callback.from_user.id
    channel_id = join_request_data.get(user_id)

    if channel_id:
        await approve(bot, user_id, channel_id)
        await callback.answer("Ваша заявка одобрена!")
        join_request_data.pop(user_id, None)
    else:
        await callback.answer("Ошибка: данные не найдены.")

async def func_join_request(join_request: ChatJoinRequest, bot: Bot):
    send_count1 = 5
    send_count2 = 5
    user_id = join_request.from_user.id
    channel_id = join_request.chat.id
    bot_info = await bot.get_me()
    bot_id = bot_info.id
    # Сохраняем данные в глобальном словаре
    join_request_data[user_id] = channel_id

    # Отправляем приветственные сообщения пользователю

    for i in range(1, send_count1 + 1):
        if not await is_user_member(bot, user_id, channel_id):
            await pic_spam(bot, user_id, str(i), keyboards[bot_id])
        await asyncio.sleep(15)
    for i in range(1, send_count2 + 1):
        if not await is_user_member(bot, user_id, channel_id):
            await spam(bot, user_id)
        await asyncio.sleep(15)

async def func_bot_add(update: types.ChatMemberUpdated, bot: Bot):
    chat = update.chat
    new_status = update.new_chat_member.status
    await update_channel_file(str(chat.id), chat.title, new_status, bot)


async def func_link_handler(msg: Message, bot: Bot):
    await msg.answer("Пришли текст инлайн-кнопки и её URL в одном сообщении через разделитель '$'")

async def func_user_message(msg: Message, bot: Bot):
    text = msg.text.strip()
    bot_info = await bot.get_me()
    bot_id = bot_info.id

    if bot_id not in keyboards:
        keyboards[bot_id] = Keyboard()

    if '$' not in text:
        await msg.answer("Неправильный формат! Используйте разделитель '$' между текстом кнопки и URL.")
        return

    try:
        button_text, invite_url = text.split('$', 1)
        await msg.answer(f"Твой текст: {button_text}\nТвоя ссылка: {invite_url}")
        await save_string_to_file(invite_url, f"bot_links/{bot_id}.txt")

        keyboards[bot_id].add_link(button_text, invite_url)

        await msg.answer("Кнопка с ссылкой добавлена!", reply_markup=keyboards[bot_id].get_keyboard())

    except ValueError:
        await msg.answer("Ошибка! Убедитесь, что отправили текст в формате: 'Текст кнопки$URL'.")

async def approve(bot: Bot, user_id: int, channel_id: int):
    """Подтверждает заявку на вступление в канал"""
    try:
        await bot.approve_chat_join_request(channel_id, user_id)
    except TelegramBadRequest as e:
        if "the chat can't have join requests" in str(e):
            print("Нет доступных запросов на вступление или они отключены.")
        else:
            raise

async def is_user_member(bot: Bot, user_id: int, channel_id: int) -> bool:
    """Проверяет, является ли пользователь участником канала"""
    try:
        member = await bot.get_chat_member(channel_id, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

async def update_channel_file(chat_id: str, title: str, status: str, bot: Bot):
    channel_dict = {}

    bot_info = await bot.get_me()
    bot_id = str(bot_info.id)

    with open(channel_ids_filename, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split(":")
            if len(parts) == 3:
                file_chat_id, file_title, file_bot_id = parts
                channel_dict[file_chat_id] = (file_title, file_bot_id)

    if status in ["kicked", "left"]:
        channel_dict.pop(chat_id, None)
    else:
        channel_dict[chat_id] = (title, bot_id)

async def spam(bot: Bot, user_id: int):
    """Отправляет пользователю текстовые приветственные сообщения"""
    bot_info = await bot.get_me()
    bot_id = bot_info.id

    invite_link = await get_strings_from_file(f"bot_links/{bot_id}.txt")
    for i in range(len(invite_link)):
        await bot.send_message(user_id, text_send2.format(link=invite_link[i]))
        await asyncio.sleep(15)


async def pic_spam(bot: Bot, user_id: int, filename: str, kb: Keyboard()):
    """Отправляет пользователю приветственные изображения с кнопкой 'Подтвердить'"""
    photo = types.FSInputFile(f"photos/{filename}.png")
    await bot.send_photo(
        chat_id=user_id,
        photo=photo,
        caption=text1,
        reply_markup=kb,
        parse_mode="Markdown"
    )