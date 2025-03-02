
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
    """Отправляет пользователю текстовые приветственные сообщения с ссылками из файлов в папке keybords."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))  # new_privet/
    channel_ids_dir = os.path.join(base_dir, "keybords")

    # Проверяем, существует ли папка keybords
    if not os.path.exists(channel_ids_dir):
        print(f"Папка {channel_ids_dir} не найдена.")
        return

    # Проходим по всем файлам в папке keybords
    for filename in os.listdir(channel_ids_dir):
        file_path = os.path.join(channel_ids_dir, filename)

        # Проверяем, что это файл (а не папка)
        if os.path.isfile(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    lines = file.readlines()
                    for line in lines:
                        # Разделяем строку по символу "$"
                        parts = line.strip().split("$")
                        if len(parts) >= 2:  # Убедимся, что строка содержит достаточно частей
                            link = parts[1]  # Второй элемент — это ссылка
                            try:
                                # Отправляем сообщение с ссылкой
                                await bot.send_message(user_id, f"Что там творится??!!! Вот ссылка: {link}")
                            except Exception as e:
                                print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
            except Exception as e:
                print(f"Ошибка при чтении файла {filename}: {e}")


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

async def check_subscriptions(bot, user_id: int, channels_to_subscribe: list[int]) -> bool:
    """
    Проверяет, подписан ли пользователь на все каналы из списка.
    Возвращает True, если пользователь подписан на все каналы, иначе False.
    """
    for channel_id in channels_to_subscribe:
        if not await is_user_member(bot, user_id, int(channel_id)):
            return False  # Пользователь не подписан на один из каналов
    return True  # Пользователь подписан на все каналы