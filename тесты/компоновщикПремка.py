import asyncio
from telethon import TelegramClient
from datetime import timedelta, datetime


# Ваши учетные данные для Telethon
api_id = '23873454'
api_hash = '80a659c17d4502cc26645418c63f35f1'
source_channel = '-1001609604130'  # Исходный канал
destination_channel = '-1002351200284'  # Канал для публикации
time_delta_minutes = 30  # Разница между постами (в минутах)


async def fetch_and_post_combined_message():
    """Сбор постов и публикация их в канал."""
    async with TelegramClient('session_name', api_id, api_hash) as client:
        # Получение сообщений из исходного канала
        messages = await client.get_messages(source_channel, limit=100)

        if len(messages) < 2:
            print("Недостаточно сообщений для компоновки.")
            return

        # Поиск первого поста с изображением
        first_post = None
        for msg in messages[::-1]:  # Проверяем сообщения от старых к новым
            if msg.photo:  # Проверяем, содержит ли сообщение изображение
                first_post = msg
                break

        if not first_post:
            print("Первое сообщение с изображением не найдено.")
            return

        first_time = first_post.date

        # Поиск второго поста с архивом
        second_post = None
        for msg in messages[::-1]:
            if msg == first_post:
                continue
            if 0 <= (msg.date - first_time).total_seconds() / 60 <= time_delta_minutes:
                if msg.file and (msg.file.name.endswith('.zip') or msg.file.name.endswith('.rar')):
                    second_post = msg
                    break

        if not second_post:
            print("Второе сообщение с архивом не найдено в пределах 30 минут.")
            return

        # Получение данных из постов
        image_file = await first_post.download_media()  # Скачиваем изображение
        archive_file = await second_post.download_media()  # Скачиваем архив
        caption = first_post.text or "Без подписи"

        # Публикация скомпонованного сообщения
        await client.send_file(
            destination_channel,
            file=image_file,
            caption=f"{caption}\n\nПрикрепленный архив ниже.",
        )
        await client.send_file(destination_channel, file=archive_file)

        print("Сообщение успешно опубликовано.")


if __name__ == "__main__":
    asyncio.run(fetch_and_post_combined_message())
