import asyncio
import logging

from aiogram import types
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from text.caption_text import text_send2, text1
from utils.file_utils import get_strings_from_file

async def is_user_member(bot, user_id: int, channel_id: int) -> bool:
    """Проверяет, является ли пользователь участником канала"""
    try:
        member = await bot.get_chat_member(channel_id, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

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

import os

async def spam(bot, user_id: int):
    """Отправляет пользователю текстовые приветственные сообщения с ссылками из .txt файлов в папке keybords."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))  # new_privet/
    channel_ids_dir = os.path.join(base_dir, "keybords")

    # Проверяем, существует ли папка keybords
    if not os.path.exists(channel_ids_dir):
        print(f"Папка {channel_ids_dir} не найдена.")
        return

    # Проходим по всем файлам в папке keybords
    for filename in os.listdir(channel_ids_dir):
        # Проверяем, что файл имеет расширение .txt
        if filename.endswith(".txt"):
            file_path = os.path.join(channel_ids_dir, filename)

            # Проверяем, что это файл (а не папка)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        lines = file.readlines()
                        for line in lines:
                            # Убираем лишние пробелы и символы новой строки
                            line = line.strip()

                            # Проверяем, что строка содержит разделитель "$"
                            if "$" in line:
                                # Разделяем строку по символу "$"
                                parts = line.split("$")

                                # Проверяем, что строка содержит достаточно частей
                                if len(parts) >= 2:
                                    link = parts[1].strip()  # Второй элемент — это ссылка

                                    # Проверяем, что ссылка не пустая
                                    if link:
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
    for channel_id in channels_to_subscribe:
        if not await is_user_member(bot, user_id, int(channel_id)):
            return False  # Пользователь не подписан на один из каналов
    return True  # Пользователь подписан на все каналы

async def get_accept_type(bot_id: int, channel_id) -> bool:
    lines = await get_strings_from_file(f"bot_channel_ids/{bot_id}.txt")
    logger.info(f"Файл bot_channel_ids/{bot_id}.txt успешно открыт")
    for line in lines:
        parts = line.strip().split(":")
        if len(parts) >= 4 and parts[0] == str(channel_id):
            accept_immediately = parts[3].lower() == "true"
            logger.info(f"Найдено значение accept_immediately: {accept_immediately}")
            return accept_immediately
            break
    else:
        logger.info("Канал не найден, используем значение по умолчанию: True")
        return True



async def send_creo_spam(bot, user_id: int, channel_id: int, send_count: int, sleep_time: int,
                         video_path: str, video_caption: str, but_text: str,
                         urlb: str, vpuskat: int):
    if not video_path or not video_caption:
        logger.error("Видео или подпись не установлены. Используйте команды /setvideocreo и /setcaptiontovideo.")
        return

    # Разбиваем but_text на отдельные кнопки
    buttons = []
    for line in but_text.strip().split("\n"):
        if "$" in line:
            text, url = line.split("$", 1)
            buttons.append({"text": text.strip(), "url": url.strip()})
        else:
            logger.warning(f"Неправильный формат строки: {line}. Пропускаю.")

    if not buttons:
        logger.error("Нет данных для создания кнопок.")
        return

    for i in range(1, send_count + 1):
        if not await is_user_member(bot, user_id, channel_id):
            try:
                builder = InlineKeyboardBuilder()

                # Добавляем кнопки в билдер
                for button in buttons:
                    builder.button(text=button["text"], url=button["url"])

                # Строим клавиатуру
                kb = builder.as_markup()

                # Отправляем видео с подписью и клавиатурой
                video = FSInputFile(video_path)
                await bot.send_video(
                    chat_id=user_id,
                    video=video,
                    caption=video_caption,
                    parse_mode="HTML",
                    reply_markup=kb
                )
                logger.info(f"Сообщение {i} успешно отправлено пользователю {user_id}. Сплю {sleep_time} секунд")

                # Проверяем, нужно ли одобрять заявку
                if not await is_user_member(bot, user_id, channel_id):
                    if vpuskat:
                        await approve(bot, user_id, channel_id)

                # Задержка между отправками
                await asyncio.sleep(sleep_time)

            except TelegramForbiddenError as e:
                # Пользователь заблокировал бота
                logger.error(f"Пользователь {user_id} заблокировал бота. Остановка отправки сообщений.")
                break
            except TelegramBadRequest as e:
                # Пользователь уже является участником канала
                if "user is already a participant" in str(e):
                    logger.info(f"Пользователь {user_id} уже является участником канала. Остановка отправки сообщений.")
                    break
                else:
                    logger.error(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
            except Exception as e:
                # Другие ошибки
                logger.error(f"Неизвестная ошибка при отправке сообщения пользователю {user_id}: {e}")
        else:
            logger.info(f"Пользователь {user_id} уже является участником канала. Остановка отправки сообщений.")
            break


