from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import re
import asyncio
from collections import Counter

# Укажите ваши API ID и API Hash
api_id = '23873454'
api_hash = '80a659c17d4502cc26645418c63f35f1'
phone_number = '+6285602959490'  # Например, '+1234567890'
source_channel = 'https://t.me/+CXhwWk5gDTA5ZGIy'  # Канал, откуда берем посты
destination_channel = 'https://t.me/addavalki'  # Канал, куда отправляем обновленные посты

client = TelegramClient('session_name', api_id, api_hash)

# Регулярное выражение для поиска ссылок
url_pattern = re.compile(r'\b(?:https?://[^\s]+)\b')

async def choose_deletion_method():
    print("Выберите способ удаления сообщений:")
    print("1. Удаление полных дубликатов сообщений.")
    print("2. Удаление сообщений с 3 и более одинаковыми словами.")
    
    method = input("Введите номер метода (1 или 2): ").strip()
    
    if method == '1':
        return "full_duplicates"
    elif method == '2':
        return "repeated_words"
    else:
        print("Некорректный ввод. Используется метод по умолчанию (полные дубликаты).")
        return "full_duplicates"

async def get_ad_posts_count():
    try:
        count = int(input("Введите количество рекламных постов для копирования: ").strip())
        return count
    except ValueError:
        print("Некорректный ввод. Будет использоваться значение по умолчанию (0).")
        return 0

async def replace_links(text, new_link):
    """Функция для замены всех ссылок на новую."""
    return re.sub(url_pattern, new_link, text)

async def copy_ads(ad_posts_count, user_link, new_link):
    """Функция для копирования рекламных постов."""
    # Получаем последние рекламные посты
    messages = await client.get_messages(user_link, limit=ad_posts_count)

    for message in messages:
        # Проверяем, есть ли в сообщении более одной ссылки
        links = url_pattern.findall(message.text)
        if len(links) > 1:  # Если в посте больше 1 ссылки, считаем его рекламным
            print(f"Найден рекламный пост с ID {message.id}")

            # Заменяем все ссылки на новый
            new_text = await replace_links(message.text, new_link)

            # Копируем медиа (если оно есть)
            if message.media:
                # Если это изображение
                if isinstance(message.media, MessageMediaPhoto):
                    await client.send_message(destination_channel, new_text, file=message.media)
                # Если это видео или документ
                elif isinstance(message.media, MessageMediaDocument):
                    await client.send_message(destination_channel, new_text, file=message.media)
                else:
                    await client.send_message(destination_channel, new_text, file=message.media)
            else:
                # Если медиа нет, просто отправляем текст
                await client.send_message(destination_channel, new_text)
        
        await asyncio.sleep(1)  # Задержка между сообщениями

    print("Все рекламные посты обработаны.")

async def delete_old_duplicates(deletion_method):
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


async def process_and_repost_messages():
    await client.start(phone_number)
    source_entity = await client.get_entity(source_channel)
    destination_entity = await client.get_entity(destination_channel)
    
    async for message in client.iter_messages(source_entity):
        if message.text:
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
        
        await asyncio.sleep(1)  # Задержка между сообщениями

    print("Все сообщения обработаны.")


async def main():
    print("Выберите действие:")
    print("1. Удалить дубликаты сообщений")
    print("2. Переслать посты без ссылок")
    print("3. копирование рек")
    choice = input("Введите 1 или 2 или 3: ").strip()
    
    if choice == '1':
        print("Вы выбрали удаление дубликатов.")
        deletion_method = await choose_deletion_method()
        await delete_old_duplicates(deletion_method)
    elif choice == '2':
        print("Вы выбрали пересылку постов без ссылок.")
        await process_and_repost_messages()
    elif choice == '3':
        print("Вы выбрали копирование рекламных постов.")
        user_link = source_channel
        ad_posts_count = 5  # Укажите количество рекламных постов для копирования
        new_link = "https://newlink.com"  # Новый URL для замены
        if ad_posts_count > 0:
            await copy_ads(ad_posts_count, user_link, new_link)
        else:
            print("\033[31mКоличество рекламных постов для копирования должно быть больше 0.\033[0m")
    else:
        print("Некорректный выбор. Пожалуйста, выберите 1 или 2.")

# Запуск основного цикла
with client:
    client.loop.run_until_complete(main())
