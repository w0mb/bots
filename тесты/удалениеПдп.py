import asyncio
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import UserNotParticipantError

# Укажите ваши данные API Telegram
API_ID = '23873454'
API_HASH = '80a659c17d4502cc26645418c63f35f1'
CHANNEL_ID = '-1001609604130'  # Например, "@example_channel" или ID

SUBSCRIBES_FILE = "../subscriptions.txt"  # Имя файла с подписками

# Функция для чтения данных из файла
def read_subscriptions(file_path):
    subscriptions = []
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line:
                    username, date_str = line.split(",")
                    subscriptions.append((username.strip(), datetime.strptime(date_str.strip(), "%Y-%m-%d")))
    except FileNotFoundError:
        print(f"Файл {file_path} не найден. Проверьте его наличие.")
    except ValueError as e:
        print(f"Ошибка чтения строки: {e}")
    return subscriptions

# Функция для удаления пользователей с истёкшей подпиской
async def remove_expired_users(client):
    today = datetime.now().date()
    subscriptions = read_subscriptions(SUBSCRIBES_FILE)

    for username, expiry_date in subscriptions:
        if expiry_date.date() < today:  # Проверяем, истёк ли срок подписки
            try:
                print(f"Удаление пользователя @{username} с истёкшей подпиской (дата: {expiry_date.date()})...")
                await client.kick_participant(CHANNEL_ID, username)  # Удаляем пользователя
                print(f"Пользователь @{username} успешно удалён.")
            except UserNotParticipantError:
                print(f"Пользователь @{username} не найден в канале.")
            except Exception as e:
                print(f"Ошибка при удалении пользователя @{username}: {e}")

# Основная функция
async def main():
    async with TelegramClient('bot_session', API_ID, API_HASH) as client:
        await remove_expired_users(client)

# Планировщик запуска
if __name__ == "__main__":
    print("Запуск проверки...")
    asyncio.run(main())
