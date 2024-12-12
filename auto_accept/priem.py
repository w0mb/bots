from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, filters, ChatMemberHandler, ChatJoinRequestHandler
import json
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from functools import partial
import nest_asyncio
from datetime import datetime
from telegram import Update, Bot, ChatMember


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


async def accept_request(update: Update, context):
    # Получаем ID канала и пользователя, который подал заявку
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id

    channels = load_channels()["channels"]
    for channel in channels:
        if channel["id"] == str(chat_id):  # Проверяем, что канал совпадает
            # Если включено автопринятие или не превышен лимит
            if channel["auto_accept"] or channel["accepted_today"] < channel["daily_limit"]:
                # Если автопринятие включено, или лимит заявок не превышен, принимаем пользователя
                await context.bot.promote_chat_member(chat_id, user_id, can_post_messages=True)
                # Увеличиваем количество принятых заявок
                channel["accepted_today"] += 1
                save_channels({"channels": channels})
                await update.message.reply_text(f"Заявка от {user_id} принята в канал {channel['name']}.")
                return
            else:
                await update.message.reply_text(f"Лимит заявок для канала {channel['name']} достигнут.")
                return
    await update.message.reply_text("Этот канал не найден.")
# Обработчик новых сообщений и заявок
async def handle_new_member(update: Update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    channels = load_channels()["channels"]
    for channel in channels:
        if channel["id"] == str(chat_id):
            await process_request(channel["id"], user_id)
            break


# Принятие заявки
async def process_request(channel_id, user_id):
    channels = load_channels()["channels"]  # Загружаем актуальные данные
    for channel in channels:
        if str(channel["id"]) == str(channel_id):
            print(f"Обнаружен канал: {channel}")  # Отладка
            if channel["auto_accept"]:
                print(f"Автоприем включен для {channel['name']}.")
            else:
                print(f"Автоприем отключен для {channel['name']}.")
            # Проверяем настройку автоприема
            if channel["auto_accept"] and channel["accepted_today"] < channel["daily_limit"]:
                bot = Bot(token='8188712922:AAHyTWd6xgxOwEbYTS7oAlLNl-2_oLOleyQ')
                await bot.approve_chat_join_request(chat_id=channel_id, user_id=user_id)
                channel["accepted_today"] += 1
                save_channels({"channels": channels})  # Сохраняем изменения
                print(f"Заявка принята в канал {channel['name']}.")
            else:
                print(f"Лимит заявок для канала {channel['name']} исчерпан или автоприем отключен.")
            return
    print("Канал не найден.")


async def handle_chat_join_request(update, context):
    chat_id = update.chat_join_request.chat.id
    user_id = update.chat_join_request.from_user.id
    print(f"Получена заявка от пользователя {user_id} в чат {chat_id}")
    await process_request(chat_id, user_id)

async def get_channels():
    # Загрузка каналов из JSON или базы данных
    return load_channels()["channels"]

async def schedule_requests():
    channels = await get_channels()
    
    # Инициализация планировщика
    scheduler = AsyncIOScheduler()

    # Запуск планировщика
    scheduler.start()
    print("Планировщик запущен.") 
    for channel in channels:
        scheduler.add_job(partial(reset_daily_limits_if_needed, channels), 'interval', seconds=86400)  # Ежедневный сброс лимитов

# Возврат в главное меню настроек
async def back_to_settings(update, context):
    await update.callback_query.answer()
    await settings(update.callback_query, context)
nest_asyncio.apply()
# Основная функция
async def main():
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




    application.add_handler(conv_handler_add_channel)  # Обработчик для добавления канала
    application.add_handler(conv_handler_set_limit)  # Обработчик для установки лимита

    application.add_handler(CallbackQueryHandler(delete_channel, pattern="^delete_channel$"))
    application.add_handler(CallbackQueryHandler(process_delete_channel, pattern="^delete_"))
    application.add_handler(CallbackQueryHandler(manage_channel, pattern="^manage_"))
    application.add_handler(CallbackQueryHandler(toggle_auto_accept, pattern="^toggle_auto_accept_"))
    application.add_handler(CallbackQueryHandler(back_to_settings, pattern="^back_to_settings$"))
    application.add_handler(ChatJoinRequestHandler(handle_chat_join_request))
    print("Бот настроен. Запуск polling...")
    await schedule_requests()
    await application.run_polling()
    

if __name__ == "__main__":
    asyncio.run(main())

