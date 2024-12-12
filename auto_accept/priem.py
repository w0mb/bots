from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, filters
import json
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# Загрузка и сохранение данных из/в .json
def load_channels():
    try:
        with open('channels.json', 'r') as f:
            channels = json.load(f)
            print("Данные каналов загружены: ", channels)  # Отладка
            return channels
    except FileNotFoundError:
        print("Файл channels.json не найден.")  # Отладка
        return {"channels": []}

def save_channels(data):
    with open('channels.json', 'w') as f:
        json.dump(data, f, indent=4)
        print("Данные каналов сохранены: ", data)  # Отладка

# Стартовая команда /settings
async def settings(update, context):
    channels = load_channels()["channels"]
    keyboard = []
    for channel in channels:
        keyboard.append([InlineKeyboardButton(channel["name"], callback_data=f"manage_{channel['name']}")])

    keyboard.append([InlineKeyboardButton("Добавить канал", callback_data="add_channel")])
    keyboard.append([InlineKeyboardButton("Удалить канал", callback_data="delete_channel")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите канал для управления или добавьте/удалите канал:', reply_markup=reply_markup)

# Добавить канал
async def add_channel(update, context):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("Введите название канала:")
    return "WAITING_FOR_NAME"

# Обработчик ввода названия канала
async def process_add_channel_name(update, context):
    context.user_data['channel_name'] = update.message.text  # Получаем название канала
    await update.message.reply_text("Введите ID канала:")
    return "WAITING_FOR_ID"

# Обработчик ввода ID канала
async def process_add_channel_id(update, context):
    channel_name = context.user_data['channel_name']
    channel_id = update.message.text  # Получаем ID канала
    channels = load_channels()["channels"]
    channels.append({"name": channel_name, "id": channel_id, "auto_accept": True, "daily_limit": 200, "accepted_today": 0})
    save_channels({"channels": channels})
    await update.message.reply_text(f"Канал {channel_name} добавлен!")
    return ConversationHandler.END

# Удалить канал
async def delete_channel(update, context):
    await update.callback_query.answer()
    channels = load_channels()["channels"]
    keyboard = []
    for channel in channels:
        keyboard.append([InlineKeyboardButton(channel["name"], callback_data=f"delete_{channel['name']}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text('Выберите канал для удаления:', reply_markup=reply_markup)

# Обработчик удаления канала
async def process_delete_channel(update, context):
    channel_name = update.callback_query.data.split("_")[1]
    channels = load_channels()["channels"]
    channels = [channel for channel in channels if channel["name"] != channel_name]
    save_channels({"channels": channels})
    await update.callback_query.answer(f"Канал {channel_name} удален.")
    return ConversationHandler.END

# Меню управления каналом
# Меню управления каналом
async def manage_channel(update, context):
    await update.callback_query.answer()
    channel_name = update.callback_query.data.split("_")[1]

    channels = load_channels()["channels"]

    for channel in channels:
        if channel["name"] == channel_name:
            print(f"Управление каналом: {channel_name}")  # Отладка: Проверяем, что кнопка для лимита появляется
            keyboard = [
                [InlineKeyboardButton("Включить/Выключить автопринятие", callback_data=f"toggle_auto_accept_{channel['id']}")],
                [InlineKeyboardButton("Установить лимит заявок", callback_data=f"set_daily_limit_{channel['id']}")],
                [InlineKeyboardButton("Назад", callback_data="back_to_settings")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.message.reply_text(f"Управление каналом: {channel_name}", reply_markup=reply_markup)
            return

    await update.callback_query.message.reply_text("Ошибка: канал не найден.")


# Включить/выключить автопринятие
async def toggle_auto_accept(update, context):
    await update.callback_query.answer()
    callback_data = update.callback_query.data
    parts = callback_data.split("_")
    channel_id = parts[-1]
    channels = load_channels()["channels"]
    
    for channel in channels:
        if channel["id"] == channel_id:
            channel["auto_accept"] = not channel["auto_accept"]
            state = "включено" if channel["auto_accept"] else "выключено"
            save_channels({"channels": channels})
            await update.callback_query.message.reply_text(f"Автопринятие для {channel['name']} теперь {state}.")
            return

    await update.callback_query.message.reply_text("Ошибка: канал не найден.")

# Установка дневного лимита заявок
# Установка дневного лимита заявок
# Установка дневного лимита заявок
async def set_daily_limit(update, context):
    callback_data = update.callback_query.data
    parts = callback_data.split("_")
    channel_id = parts[-1]
    context.user_data['current_channel_id'] = channel_id
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("Введите новый лимит заявок в день:")
    return "WAITING_FOR_LIMIT"  # Переход к состоянию, которое ждет ввода лимита




# Обработка ввода дневного лимита
# Обработка ввода дневного лимита
# Обработка ввода дневного лимита
async def process_daily_limit(update, context):
    try:
        daily_limit = int(update.message.text)  # Получаем введенный лимит
        channel_id = context.user_data['current_channel_id']  # Извлекаем ID канала

        # Загружаем данные каналов из JSON
        channels = load_channels()["channels"]
        
        # Ищем канал по ID и обновляем лимит
        for channel in channels:
            if channel["id"] == channel_id:
                print(f"Обновляем канал {channel['name']} с текущим лимитом: {channel['daily_limit']}")  # Отладка
                # Обновляем лимит
                channel["daily_limit"] = daily_limit
                save_channels({"channels": channels})

                # Подтверждаем обновление лимита пользователю
                await update.message.reply_text(f"Лимит заявок для канала {channel['name']} обновлен на {daily_limit} заявок в день.")
                break

    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное число.")
        return "WAITING_FOR_LIMIT"  # Оставляем состояние, чтобы пользователь мог повторить ввод

    return ConversationHandler.END  # Завершаем разговор

def reset_limits_daily():
    channels = load_channels()["channels"]
    channels = reset_daily_limits_if_needed(channels)  # Сбрасываем лимиты
    save_channels({"channels": channels})

def reset_daily_limits_if_needed(channels):
    current_date = datetime.now().date()
    for channel in channels:
        last_reset_date = datetime.strptime(channel.get("last_reset", "1970-01-01"), "%Y-%m-%d").date()
        
        if last_reset_date != current_date:
            # Сброс лимита
            channel["accepted_today"] = 0
            channel["last_reset"] = current_date.strftime("%Y-%m-%d")
    
    return channels

# Проверка лимита и принятие заявки
async def accept_request(channel_id):
    channels = load_channels()["channels"]
    channels = reset_daily_limits_if_needed(channels)  # Сбрасываем лимиты, если нужно

    for channel in channels:
        if channel["id"] == channel_id:
            if channel["accepted_today"] < channel["daily_limit"]:
                channel["accepted_today"] += 1
                save_channels({"channels": channels})
                return True  # Заявка принята
            else:
                return False  # Лимит достигнут
    return False  # Канал не найден
# Принятие заявки
async def process_request(update, context):
    channel_id = context.user_data['current_channel_id']  # Извлекаем ID канала

    # Пробуем принять заявку
    if await accept_request(channel_id):
        await update.message.reply_text(f"Заявка принята в канал {channel_id}.")
    else:
        await update.message.reply_text(f"Лимит заявок для канала {channel_id} достигнут на сегодня.")



# Возврат в главное меню настроек
async def back_to_settings(update, context):
    await update.callback_query.answer()
    await settings(update.callback_query, context)

# Основная функция
def main():
    application = Application.builder().token('8188712922:AAHyTWd6xgxOwEbYTS7oAlLNl-2_oLOleyQ').build()

    application.add_handler(CommandHandler('settings', settings))

    conv_handler_add_channel = ConversationHandler(
        entry_points=[CallbackQueryHandler(add_channel, pattern="^add_channel$")],
        states={
            "WAITING_FOR_NAME": [MessageHandler(filters.TEXT, process_add_channel_name)],
            "WAITING_FOR_ID": [MessageHandler(filters.TEXT, process_add_channel_id)],
        },
        fallbacks=[CallbackQueryHandler(back_to_settings, pattern="^back_to_settings$")]
    )
    conv_handler_set_limit = ConversationHandler(
    entry_points=[CallbackQueryHandler(set_daily_limit, pattern="^set_daily_limit_")],
    states={
        "WAITING_FOR_LIMIT": [MessageHandler(filters.TEXT, process_daily_limit)],
    },
    fallbacks=[CallbackQueryHandler(back_to_settings, pattern="^back_to_settings$")]
    )


    scheduler = AsyncIOScheduler()
    scheduler.add_job(some_task, 'interval', seconds=10)  # Пример задачи, которая выполняется каждые 10 секунд

    # Запускаем планировщик
    scheduler.start()

    # Запускаем цикл событий asyncio
    loop = asyncio.get_event_loop()
    loop.run_forever()  # Цикл будет работать бесконечно, ожидая выполнения задач


    application.add_handler(conv_handler_add_channel)  # Обработчик для добавления канала
    application.add_handler(conv_handler_set_limit)  # Обработчик для установки лимита

    application.add_handler(CallbackQueryHandler(delete_channel, pattern="^delete_channel$"))
    application.add_handler(CallbackQueryHandler(process_delete_channel, pattern="^delete_"))
    application.add_handler(CallbackQueryHandler(manage_channel, pattern="^manage_"))
    application.add_handler(CallbackQueryHandler(toggle_auto_accept, pattern="^toggle_auto_accept_"))
    application.add_handler(CallbackQueryHandler(back_to_settings, pattern="^back_to_settings$"))


    application.run_polling()

if __name__ == '__main__':
    main()
