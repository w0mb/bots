import asyncio
from telethon import TelegramClient

# Ваши учетные данные для Telethon
api_id = '23873454'
api_hash = '80a659c17d4502cc26645418c63f35f1'
source_channel = 'https://t.me/+tZ_KQwkIHIc0ZWUy'  # Исходный канал
destination_channel = 'https://t.me/+W1qZqGrp9dk0YzUy'  # Канал для публикации

async def fetch_and_post_combined_message():
    async with TelegramClient('session_name', api_id, api_hash) as client:
        messages = await client.get_messages(source_channel, limit=100)

        if len(messages) < 2:
            print("Недостаточно сообщений для анализа.")
            return

        print("Анализируем доступные сообщения...")

        # Поиск последовательности фото -> архив
        first_post = None
        second_post = None

        for i in range(len(messages) - 1):  # Проверяем пары сообщений
            msg1 = messages[i]
            msg2 = messages[i + 1]

            if msg1.photo and msg2.file and (
                (msg2.file.name and (msg2.file.name.endswith('.zip') or msg2.file.name.endswith('.rar')))
                or msg2.file.mime_type in ['application/zip', 'application/x-rar-compressed']
            ):
                first_post = msg1
                second_post = msg2
                break  # Выходим, как только найдём нужную пару

        if not (first_post and second_post):
            print("Не найдена последовательность Фото → Архив.")
            return

        # Скачивание и публикация
        image_file = await first_post.download_media()
        archive_file = await second_post.download_media()

        caption = first_post.text or " "

        # Публикация фото с текстом
        await client.send_file(
            destination_channel,
            file=image_file,
            caption=f"{caption}\n\nПрикрепленный архив ниже.",
        )

        # Публикация архива
        await client.send_file(destination_channel, file=archive_file)

        print("Сообщения успешно опубликованы.")

if __name__ == "__main__":
    asyncio.run(fetch_and_post_combined_message())
