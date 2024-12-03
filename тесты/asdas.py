import json
import argparse
from telethon import TelegramClient
import asyncio

# Ваши данные API
api_id = '23873454'
api_hash = '80a659c17d4502cc26645418c63f35f1'

# Файл для хранения ID опубликованных сообщений
POSTED_IDS_FILE = "posted_ids.json"

# Загрузка списка опубликованных сообщений
def load_posted_ids():
    try:
        with open(POSTED_IDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Сохранение списка опубликованных сообщений
def save_posted_ids(posted_ids):
    with open(POSTED_IDS_FILE, "w", encoding="utf-8") as f:
        json.dump(posted_ids, f, ensure_ascii=False, indent=4)

async def copy_posts(source_channel, destination_channel, count):
    client = TelegramClient('session_name', api_id, api_hash)
    await client.start()

    # Загрузка состояния опубликованных постов
    posted_ids = load_posted_ids()
    if source_channel not in posted_ids:
        posted_ids[source_channel] = []

    try:
        async for message in client.iter_messages(source_channel, limit=100):  # Увеличьте `limit`, если нужно
            if message.id in posted_ids[source_channel]:
                print(f"Сообщение с ID {message.id} уже было опубликовано. Пропускаем.")
                continue

            # Отправляем сообщение в канал назначения
            await client.send_message(destination_channel, message.text)
            print(f"Сообщение с ID {message.id} опубликовано.")
            
            # Обновляем список опубликованных сообщений
            posted_ids[source_channel].append(message.id)
            save_posted_ids(posted_ids)

            count -= 1
            if count <= 0:
                break

    finally:
        await client.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Копирование сообщений из одного канала в другой.")
    parser.add_argument("--source", required=True, help="Ссылка на исходный канал.")
    parser.add_argument("--destination", required=True, help="Ссылка на канал назначения.")
    parser.add_argument("--count", type=int, default=1, help="Количество сообщений для копирования.")
    args = parser.parse_args()

    asyncio.run(copy_posts(args.source, args.destination, args.count))
