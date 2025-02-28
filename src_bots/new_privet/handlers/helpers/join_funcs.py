import asyncio
import os

from aiogram import types
from aiogram.exceptions import TelegramBadRequest

from src_bots.new_privet.text.caption_text import text_send2, text1
from src_bots.new_privet.utils.file_utils import get_strings_from_file

async def is_user_member(bot, user_id: int, channel_id: int) -> bool:
    """Проверяет, является ли пользователь участником канала"""
    try:
        member = await bot.get_chat_member(channel_id, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

async def update_channel_file(chat_id: str, title: str, status: str, bot):
    channel_dict = {}

    bot_info = await bot.get_me()
    bot_id = str(bot_info.id)

    # Получаем путь к директории и файлу
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))  # new_privet/
    channel_ids_dir = os.path.join(base_dir, "bot_channel_ids")
    channel_ids_filename = os.path.join(channel_ids_dir, f"{bot_id}.txt")

    # Создаём директорию, если её нет
    os.makedirs(channel_ids_dir, exist_ok=True)

    # Проверяем существование файла
    if os.path.exists(channel_ids_filename):
        with open(channel_ids_filename, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(":")
                if len(parts) == 3:
                    file_chat_id, file_title, file_bot_id = parts
                    channel_dict[file_chat_id] = (file_title, file_bot_id)
    else:
        open(channel_ids_filename, "x", encoding="utf-8").close()  # Создаём файл
        # Повторно читаем файл (хотя он пустой, но для логики)
        with open(channel_ids_filename, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(":")
                if len(parts) == 3:
                    file_chat_id, file_title, file_bot_id = parts
                    channel_dict[file_chat_id] = (file_title, file_bot_id)

    # Обновляем словарь
    if status in ["kicked", "left"]:
        channel_dict.pop(chat_id, None)
    else:
        channel_dict[chat_id] = (title, bot_id)

    # Сохраняем изменения
    with open(channel_ids_filename, "w", encoding="utf-8") as file:
        for chat_id, (title, bot_id) in channel_dict.items():
            file.write(f"{chat_id}:{title}:{bot_id}\n")


    # Перезаписываем файл с обновленными данными
    with open(channel_ids_filename, "w", encoding="utf-8") as file:
        for chat_id, (title, bot_id) in channel_dict.items():
            file.write(f"{chat_id}:{title}:{bot_id}\n")

async def spam(bot, user_id: int):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))  # new_privet/
    channel_ids_dir = os.path.join(base_dir, f"bot_links/")

    """Отправляет пользователю текстовые приветственные сообщения"""
    bot_info = await bot.get_me()
    bot_id = bot_info.id
    channel_ids_filename = os.path.join(channel_ids_dir, f"{bot_id}.txt")
    invite_link = await get_strings_from_file(channel_ids_filename)
    for i in range(len(invite_link)):
        await bot.send_message(user_id, text_send2.format(link=invite_link[i]))
        await asyncio.sleep(15)


async def pic_spam(bot, user_id: int, filename: str, kb):
    """Отправляет пользователю приветственные изображения с кнопкой 'Подтвердить'"""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    channel_ids_dir = os.path.join(base_dir, f"photos/")
    channel_ids_filename = os.path.join(channel_ids_dir, f"{filename}.txt")

    photo = types.FSInputFile(channel_ids_filename)
    await bot.send_photo(
        chat_id=user_id,
        photo=photo,
        caption=text1,
        reply_markup=kb,
        parse_mode="Markdown"
    )

async def approve(bot, user_id: int, channel_id: int):
    """Подтверждает заявку на вступление в канал"""
    try:
        await bot.approve_chat_join_request(channel_id, user_id)
    except TelegramBadRequest as e:
        if "the chat can't have join requests" in str(e):
            print("Нет доступных запросов на вступление или они отключены.")
        else:
            raise