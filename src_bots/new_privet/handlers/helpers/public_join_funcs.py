from pathlib import Path


async def public_update_channel_file(chat_id: str | None, title: str | None, status: str | None, bot, accept_statuss=False):
    channel_dict = {}

    bot_info = await bot.get_me()
    bot_id = str(bot_info.id)

    # Получаем путь к директории и файлу
    base_dir = Path(__file__).parent.parent.parent  # new_privet/
    channel_ids_dir = base_dir / "public_bot_channel_ids"
    channel_ids_filename = channel_ids_dir / f"{bot_id}.txt"

    # Создаём директорию, если её нет
    channel_ids_dir.mkdir(exist_ok=True)

    # Чтение файла и обновление словаря
    if channel_ids_filename.exists():
        with open(channel_ids_filename, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(":")
                if len(parts) == 4:
                    file_chat_id, file_title, file_bot_id, accept_status = parts
                    channel_dict[file_chat_id] = (file_title, file_bot_id, accept_status)

    # Обновление словаря
    if status in ["kicked", "left"]:
        if chat_id is not None:
            channel_dict.pop(chat_id, None)
    else:
        channel_dict[chat_id] = (title, bot_id, accept_statuss)

    # Запись обновленного словаря в файл
    with open(channel_ids_filename, "w", encoding="utf-8") as file:
        for chat_id, (title, bot_id, accept_statuss) in channel_dict.items():
            file.write(f"{chat_id}:{title}:{bot_id}:{accept_statuss}\n")