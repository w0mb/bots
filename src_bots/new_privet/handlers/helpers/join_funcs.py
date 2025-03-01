import asyncio
import os

from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from playwright.sync_api import expect

from src_bots.new_privet.text.caption_text import text_send2, text1
from src_bots.new_privet.utils.file_utils import get_strings_from_file

async def is_user_member(bot, user_id: int, channel_id: int) -> bool:
    """Проверяет, является ли пользователь участником канала"""
    try:
        member = await bot.get_chat_member(channel_id, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

import os
from pathlib import Path

async def update_channel_file(chat_id: str | None, title: str | None, status: str | None, bot, accept_statuss=False):
    channel_dict = {}

    bot_info = await bot.get_me()
    bot_id = str(bot_info.id)

    # Получаем путь к директории и файлу
    base_dir = Path(__file__).parent.parent.parent  # new_privet/
    channel_ids_dir = base_dir / "bot_channel_ids"
    channel_ids_filename = channel_ids_dir / f"{bot_id}.txt"

    # Создаём директорию, если её нет
    channel_ids_dir.mkdir(exist_ok=True)

    # Чтение файла и обновление словаря
    if channel_ids_filename.exists():
        with open(channel_ids_filename, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(":")
                if len(parts) == 4:
                    file_chat_id, file_title, file_bot_id, accept_status = parts
                    channel_dict[file_chat_id] = (file_title, file_bot_id, accept_status)

    # Обновление словаря
    if status in ["kicked", "left"]:
        if chat_id is not None:
            channel_dict.pop(chat_id, None)
    else:
        channel_dict[chat_id] = (title, bot_id, accept_statuss)

    # Запись обновленного словаря в файл
    with open(channel_ids_filename, "w", encoding="utf-8") as file:
        for chat_id, (title, bot_id, accept_statuss) in channel_dict.items():
            file.write(f"{chat_id}:{title}:{bot_id}:{accept_statuss}\n")

async def spam(bot, user_id: int):
    """Отправляет пользователю текстовые приветственные сообщения"""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))  # new_privet/
    channel_ids_dir = os.path.join(base_dir, "bot_links")

    bot_info = await bot.get_me()
    bot_id = bot_info.id
    channel_ids_filename = os.path.join(channel_ids_dir, f"{bot_id}.txt")

    invite_links = await get_strings_from_file(channel_ids_filename)

    for link in invite_links:
        try:
            await bot.send_message(user_id, text_send2.format(link=link))
        except Exception:
            print("скорее всего бота заблокали")


async def pic_spam(bot, user_id: int, filename: str, kb):
    """Отправляет пользователю приветственные изображения с кнопкой 'Подтвердить'"""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))  # new_privet/
    photos_dir = os.path.join(base_dir, "photos")

    photo_path = os.path.join(photos_dir, f"{filename}.png")  # предполагаем, что формат JPG

    if not os.path.exists(photo_path):
        print(f"Файл {photo_path} не найден.")
        return

    photo = types.FSInputFile(photo_path)
    try:
        await bot.send_photo(
            chat_id=user_id,
            photo=photo,
            caption=text1,
            reply_markup=kb,
            parse_mode="Markdown"
        )
    except Exception:
        print("скорее всего бота заблокали")


async def approve(bot, user_id: int, channel_id: int):
    """Подтверждает заявку на вступление в канал"""
    try:
        await bot.approve_chat_join_request(channel_id, user_id)
    except TelegramBadRequest as e:
        if "the chat can't have join requests" in str(e):
            print("Нет доступных запросов на вступление или они отключены.")
        else:
            raise

async def check_subscriptions(bot, user_id: int, channel_id: int) -> bool:
    """
    Проверяет, подписан ли пользователь на каналы из списка "принимаемых сразу".
    """
    file_path = f"bot_channel_ids/{bot.id}.txt"
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                parts = line.strip().split(":")
                if parts[2].lower() == "true":
                    if not await is_user_member(bot, user_id, int(parts[0])):
                        return False
            return True
    except FileNotFoundError:
        return False