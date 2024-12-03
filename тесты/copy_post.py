import argparse
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import re
import asyncio
import json

# Укажите ваши API ID и API Hash
api_id = '23873454'
api_hash = '80a659c17d4502cc26645418c63f35f1'
client = TelegramClient('session_name', api_id, api_hash)

# Файл для хранения ID опубликованных сообщений
POSTED_IDS_FILE = "posted_ids.json"
# Регулярное выражение для поиска ссылок
url_pattern = re.compile(r'\b(?:https?://[^\s]+)\b')

# Загрузка списка опубликованных сообщений
def load_posted_ids():
    try:
        with open(POSTED_IDS_FILE, "r", encoding="utf-8") as f:
            data = f.read()
            return json.loads(data) if data.strip() else {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Сохранение списка опубликованных сообщений
def save_posted_ids(posted_ids):
    with open(POSTED_IDS_FILE, "w", encoding="utf-8") as f:
        json.dump(posted_ids, f, ensure_ascii=False, indent=4)

async def process_and_repost_messages(source, destination, count):
    """Процесс получения сообщений из одного канала и отправки в другой."""
    await client.start()
    count = 1
    source_entity = await client.get_entity(source)
    destination_entity = await client.get_entity(destination)

    # Загрузка состояния опубликованных постов
    posted_ids = load_posted_ids()
    if source not in posted_ids:
        posted_ids[source] = []

    # Переменная для подсчета отправленных сообщений
    oper = 0

    async for message in client.iter_messages(source_entity):
        if oper >= count:  # Ограничение на количество постов
            break

        # Пропускаем сообщение, если оно уже было отправлено
        if message.id in posted_ids[source]:
            print(f"Пропущено сообщение с ID {message.id}, так как оно уже отправлено ранее.")
            continue

        if message.text:
            # Находим все ссылки в тексте
            links = url_pattern.findall(message.text)

            # Игнорируем сообщения с более чем одной ссылкой
            if len(links) > 1:
                print(f"Пропущено сообщение с ID {message.id}, содержит {len(links)} ссылок")
                continue

            # Разбиваем текст на строки
            lines = message.text.split('\n')

            # Отбираем строки, в которых нет ссылок
            cleaned_lines = [line for line in lines if not url_pattern.search(line)]
            cleaned_text = '\n'.join(cleaned_lines).strip()

            # Если текст после удаления строк не пустой, пересылаем его
            if cleaned_text:
                if isinstance(message.media, MessageMediaPhoto):
                    await client.send_file(destination_entity, message.media.photo, caption=cleaned_text)
                elif isinstance(message.media, MessageMediaDocument):
                    await client.send_file(destination_entity, message.media.document, caption=cleaned_text)
                else:
                    await client.send_message(destination_entity, cleaned_text, file=message.media)

                print(f"Переслано сообщение с ID {message.id} без строки с ссылкой")

                # Добавляем ID в список отправленных
                posted_ids[source].append(message.id)
                save_posted_ids(posted_ids)
                oper += 1  # Увеличиваем счетчик только после успешной отправки

        await asyncio.sleep(1)  # Задержка между сообщениями

    print("Все сообщения обработаны.")

async def main():
    # Обработка аргументов командной строки
    parser = argparse.ArgumentParser(description="Копирование постов из одного Telegram канала в другой.")
    parser.add_argument("--source", required=True, help="Ссылка на исходный Telegram-канал.")
    parser.add_argument("--destination", required=True, help="Ссылка на целевой Telegram-канал.")
    parser.add_argument("--count", type=int, required=True, help="Количество постов для публикации в серии.")
    args = parser.parse_args()

    try:
        # Запускаем основную логику
        await process_and_repost_messages(args.source, args.destination, 1)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        # Закрываем клиент после завершения работы
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
