import argparse
from telethon import TelegramClient
import re
import asyncio
from collections import Counter

# Укажите ваши API ID и API Hash
api_id = '23873454'
api_hash = '80a659c17d4502cc26645418c63f35f1'
phone_number = '+6285602959490'  # Например, '+1234567890'

client = TelegramClient('session_name', api_id, api_hash)

# Регулярное выражение для поиска ссылок
url_pattern = re.compile(r'\b(?:https?://[^\s]+)\b')
def normalize_text(text):
    return ' '.join(text.lower().strip().split())
# Функция для удаления дубликатов
async def delete_old_duplicates(destination_channel):
    await client.start(phone_number)
    entity = await client.get_entity(destination_channel)
    
    seen_texts = set()  # Словарь для хранения текста сообщений и самого нового сообщения с этим текстом
    delete_count = 0  # Счетчик удаленных сообщений

    async for message in client.iter_messages(destination_channel):
        # Пропускаем сообщения без текста
        if not message.text:
            print(f"Пропущено сообщение с ID {message.id}, так как текста нет")
            continue

        # Если текст уже был обработан, удаляем сообщение
        if message.text in seen_texts:
            await client.delete_messages(destination_channel, message.id)
            delete_count += 1
            print(f"Удалено сообщение с ID {message.id}, текст: {message.text}")
        else:
            # Добавляем текст сообщения в список обработанных
            seen_texts.add(message.text)
            print(f"Обработано сообщение с ID {message.id}, текст: {message.text}")

    print(f"Завершено удаление дубликатов. Удалено {delete_count} сообщений.")

async def main():
    # Чтение параметров командной строки
    parser = argparse.ArgumentParser(description="Удаление дубликатов сообщений из канала.")
    parser.add_argument("--channel", required=True, help="Ссылка на канал для удаления дубликатов.")
    # parser.add_argument("--deletion_method", required=True, choices=["repeated_words", "full_duplicates"], help="Метод удаления: repeated_words или full_duplicates")
    args = parser.parse_args()

    # Запуск функции удаления дубликатов с переданным методом и каналом
    await delete_old_duplicates(args.channel)

if __name__ == "__main__":
    asyncio.run(main())