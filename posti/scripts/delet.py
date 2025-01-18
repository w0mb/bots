import asyncio
from datetime import datetime
from telethon import TelegramClient

# Ваши данные API
API_ID = '23873454'
API_HASH = '80a659c17d4502cc26645418c63f35f1'
CHANNEL_ID = 'https://t.me/slituesuchu'  # ID канала (можно использовать @channel_username)
SUBSCRIBES_FILE = "C:\\Program Files (x86)\\bots\\subscriptions.txt"  # Имя файла с подписками

# Загрузка подписок из файла
def load_subscribers(file_path):
    """Загрузка пользователей из файла subscribes.txt."""
    subscribers = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    username, subscription_date = line.split(":")
                    subscribers.append((username.strip(), subscription_date.strip()))
                except ValueError:
                    print(f"Ошибка в формате строки: {line}. Пропускаем.")
                    continue
    return subscribers

# Удаление пользователей с истёкшим сроком подписки
async def remove_expired_users(client):
    today = datetime.today().date()  # Текущая дата

    # Загрузка списка пользователей
    subscribers = load_subscribers(SUBSCRIBES_FILE)

    for username, subscription_date in subscribers:
        try:
            # Преобразуем строку даты в объект datetime
            expiry_date = datetime.strptime(subscription_date, "%Y-%m-%d").date()

            # Проверяем, истёк ли срок подписки
            if expiry_date < today:
                print(f"Удаление пользователя {username}, срок подписки истёк.")
                # Ваш код для удаления пользователя из канала
                try:
                    user = await client.get_entity(username)
                    await client.kick_participant(CHANNEL_ID, user)
                    print(f"Пользователь {username} был удалён.")
                except Exception as e:
                    print(f"Не удалось удалить пользователя {username}: {e}")
        except ValueError:
            print(f"Ошибка в формате даты для пользователя {username}: {subscription_date}. Пропускаем.")

# Основная функция
async def main():
    # Создаём клиент Telethon
    client = TelegramClient('session_name', API_ID, API_HASH)

    # Подключаемся и выполняем удаление пользователей
    await client.start()
    await remove_expired_users(client)

# Запуск основного кода
if __name__ == "__main__":
    asyncio.run(main())
