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

# Функция для удаления дубликатов
async def delete_old_duplicates(deletion_method, destination_channel):
    await client.start(phone_number)
    entity = await client.get_entity(destination_channel)
    
    seen_texts = {}  # Словарь для хранения текста сообщений и самого нового сообщения с этим текстом
    delete_count = 0  # Счетчик удаленных сообщений

    async for message in client.iter_messages(entity):
        if message.text:  # Проверяем, что у сообщения есть текст
            # Логика для удаления сообщений с 3 и более одинаковыми словами
            if deletion_method == "repeated_words":
                word_list = re.findall(r'\b\w+\b', message.text.lower())  # Разбиваем текст на слова
                word_count = Counter(word_list)
                repeated_words = [word for word, count in word_count.items() if count >= 2]
                
                if repeated_words:
                    print(f"\033[33mСообщение с ID {message.id} содержит повторяющиеся слова: {repeated_words}\033[0m")
                    # Если есть повторяющиеся слова, считаем сообщение дубликатом
                    await client.delete_messages(entity, message.id)
                    delete_count += 1
                    print(f"\033[31mУдалено сообщение с ID {message.id}, дата отправки: {message.date}, текст: {message.text}\033[0m")
                    print(f"\033[31mПричина удаления: Сообщение с повторяющимися словами.\033[0m")
                    continue  # Переходим к следующему сообщению

            # Логика для удаления полных дубликатов сообщений
            if deletion_method == "full_duplicates":
                if message.text in seen_texts:
                    # Если текст уже встречался, проверяем, какое из сообщений старше
                    previous_message = seen_texts[message.text]
                    if message.date < previous_message.date:
                        # Если текущее сообщение старше, удаляем его
                        await client.delete_messages(entity, message.id)
                        delete_count += 1
                        print(f"\033[31mУдалено сообщение с ID {message.id}, дата отправки: {message.date}, текст: {message.text}\033[0m")
                        print(f"\033[31mПричина удаления: Старое сообщение с дубликатом текста.\033[0m")
                    else:
                        # Иначе удаляем предыдущее сообщение и сохраняем текущее как новое
                        await client.delete_messages(entity, previous_message.id)
                        delete_count += 1
                        print(f"\033[31mУдалено сообщение с ID {previous_message.id}, дата отправки: {previous_message.date}, текст: {previous_message.text}\033[0m")
                        print(f"\033[31mПричина удаления: Новое сообщение заменило старое.\033[0m")
                        seen_texts[message.text] = message
                else:
                    # Если текст не встречался, сохраняем сообщение
                    seen_texts[message.text] = message

        # Вывод отладочной информации о текущем сообщении
        print(f"Обработано сообщение с ID {message.id}, дата отправки: {message.date}, текст: {message.text}")
        
        await asyncio.sleep(1)  # Задержка в 1 секунду между проверками

    print(f"Завершено удаление старых дубликатов. Удалено {delete_count} сообщений.")

async def main():
    # Чтение параметров командной строки
    parser = argparse.ArgumentParser(description="Удаление дубликатов сообщений из канала.")
    parser.add_argument("--channel", required=True, help="Ссылка на канал для удаления дубликатов.")
    # parser.add_argument("--deletion_method", required=True, choices=["repeated_words", "full_duplicates"], help="Метод удаления: repeated_words или full_duplicates")
    args = parser.parse_args()

    # Запуск функции удаления дубликатов с переданным методом и каналом
    await delete_old_duplicates("full_duplicates", args.channel)

if __name__ == "__main__":
    asyncio.run(main())