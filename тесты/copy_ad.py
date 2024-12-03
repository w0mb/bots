from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from telethon.errors.rpcerrorlist import FloodWaitError
import re
import asyncio
import json
import argparse

# Укажите ваши API ID и API Hash
api_id = '23873454'
api_hash = '80a659c17d4502cc26645418c63f35f1'

client = TelegramClient('session_name', api_id, api_hash)

# Регулярное выражение для поиска ссылок
url_pattern = re.compile(r'\b(?:https?://[^\s]+)\b')

# Файл для хранения ID опубликованных сообщений
POSTED_AD_IDS_FILE = "posted_ad_ids.json"


def load_posted_ad_ids():
    """Загрузка списка ID обработанных рекламных постов."""
    try:
        with open(POSTED_AD_IDS_FILE, "r", encoding="utf-8") as f:
            data = f.read()
            return json.loads(data) if data.strip() else {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_posted_ad_ids(posted_ad_ids):
    """Сохранение списка ID обработанных рекламных постов."""
    with open(POSTED_AD_IDS_FILE, "w", encoding="utf-8") as f:
        json.dump(posted_ad_ids, f, ensure_ascii=False, indent=4)


async def safe_get_entity(channel_link):
    """Безопасный вызов get_entity с обработкой FloodWaitError."""
    while True:
        try:
            return await client.get_entity(channel_link)
        except FloodWaitError as e:
            print(f"FloodWaitError: подождите {e.seconds} секунд.")
            await asyncio.sleep(e.seconds)


async def copy_ad_post(source_channel, destination_channel, new_link):
    """Функция для копирования одного рекламного поста."""
    await client.start()

    source_entity = await safe_get_entity(source_channel)
    destination_entity = await safe_get_entity(destination_channel)

    # Загрузка состояния обработанных постов
    posted_ad_ids = load_posted_ad_ids()
    if source_channel not in posted_ad_ids:
        posted_ad_ids[source_channel] = []

    async for message in client.iter_messages(source_entity):
        # Пропускаем уже обработанные сообщения
        if message.id in posted_ad_ids[source_channel]:
            print(f"Пропущено сообщение с ID {message.id}, так как оно уже обработано ранее.")
            continue

        # Проверяем, есть ли в сообщении более одной ссылки (определяем как рекламный пост)
        links = url_pattern.findall(message.text or "")
        if len(links) > 1:
            print(f"Найден рекламный пост с ID {message.id}")

            # Заменяем все ссылки на новый
            new_text = re.sub(url_pattern, new_link, message.text or "")

            try:
                # Копируем медиа (если есть)
                if message.media:
                    if isinstance(message.media, MessageMediaPhoto):
                        await client.send_file(destination_entity, message.media.photo, caption=new_text)
                    elif isinstance(message.media, MessageMediaDocument):
                        await client.send_file(destination_entity, message.media.document, caption=new_text)
                    else:
                        await client.send_file(destination_entity, message.media, caption=new_text)
                else:
                    # Если медиа нет, просто отправляем текст
                    await client.send_message(destination_entity, new_text)

                # Добавляем ID сообщения в список обработанных
                posted_ad_ids[source_channel].append(message.id)
                save_posted_ad_ids(posted_ad_ids)
                print(f"Рекламный пост с ID {message.id} успешно опубликован.")
                break  # Обрабатываем только один пост за вызов функции
            except Exception as e:
                print(f"Ошибка при отправке сообщения: {e}")

        await asyncio.sleep(1)  # Задержка между сообщениями

    print("Обработка рекламных постов завершена.")


async def main():
    parser = argparse.ArgumentParser(description="Копирование рекламных постов из одного Telegram-канала в другой.")
    parser.add_argument("--source", required=True, help="Ссылка на исходный Telegram-канал.")
    parser.add_argument("--destination", required=True, help="Ссылка на целевой Telegram-канал.")
    parser.add_argument("--new_link", required=True, help="Ссылка для замены.")
    args = parser.parse_args()

    try:
        # Обработка одного рекламного поста
        await copy_ad_post(args.source, args.destination, args.new_link)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
