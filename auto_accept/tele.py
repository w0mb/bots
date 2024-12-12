from telethon import TelegramClient, events, errors

# Ваши учетные данные API
api_id = '23873454'
api_hash = '80a659c17d4502cc26645418c63f35f1'

# Название файла сессии
session_name = 'session'

# ID или username канала
channel_username = 'https://t.me/+vGFvtQ40OMgzOTMy'

# Лимит на количество заявок
request_limit = 200

async def main():
    # Инициализация клиента
    client = TelegramClient(session_name, api_id, api_hash)
    await client.start()

    print("Клиент успешно запущен!")

    # Получаем объект канала
    try:
        channel = await client.get_entity(channel_username)
    except errors.UsernameNotOccupiedError:
        print("Канал не найден!")
        return

    # Счетчик обработанных заявок
    processed_requests = 0

    # Получаем список заявок на вступление через метод get_participants
    try:
        async for user in client.iter_participants(channel, filter=channel.participants.Requests):
            if processed_requests >= request_limit:
                print(f"Достигнут лимит из {request_limit} заявок. Завершаю работу.")
                break

            try:
                # Принимаем заявку
                await client.approve_join_request(channel, user.id)
                print(f"Заявка от {user.id} принята.")
                processed_requests += 1
            except Exception as e:
                print(f"Ошибка при обработке заявки от {user.id}: {e}")

    except errors.ChatAdminRequiredError:
        print("У аккаунта недостаточно прав для просмотра заявок!")

    await client.disconnect()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
