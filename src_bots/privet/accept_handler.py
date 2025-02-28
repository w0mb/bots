import asyncio
import logging

from aiogram import Bot, types, Router, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, ChatJoinRequest, CallbackQuery

from accept_funcs import (update_channel_file, is_user_member, pic_spam, spam,
                          approve, func_user_message, func_link_handler,
                          func_bot_add, func_join_request, func_confirm_request)
from src_bots.privet.utils import save_string_to_file


async def update_pooling(new_token: str, bots: list, dispatchers: list, tasks: list):
    """
    Добавляет нового бота в пул и запускает его.
    """
    try:
        # Создаем нового бота
        new_bot = Bot(
            token=new_token,
            default=DefaultBotProperties(parse_mode="HTML")
        )

        # Создаем новый диспетчер
        new_dp = Dispatcher()

        # Добавляем роутер в диспетчер
        new_dp.include_router(accept_handler)

        # Удаляем вебхук (если он есть)
        await new_bot.delete_webhook(drop_pending_updates=True)

        # Запускаем пуллинг для нового бота
        task = asyncio.create_task(new_dp.start_polling(new_bot))
        tasks.append(task)

        # Добавляем бота и диспетчер в списки
        bots.append(new_bot)
        dispatchers.append(new_dp)

        logging.info(f"Новый бот добавлен и запущен: {new_token}")
    except Exception as e:
        logging.error(f"Ошибка при добавлении нового бота: {e}")


accept_handler = Router()

@accept_handler.message(Command(commands=['addtoken']))
async def add_token_handler(message: Message):
    await message.answer("Пришли мне токен, чтобы я добавил его в систему.")

    @accept_handler.message()
    async def add_token_handler1(message: Message, bot: Bot):
        new_token = message.text.strip()
        if new_token:
            await save_string_to_file(new_token, "tokens.txt")

            bots = bot.__dict__.get("bots", [])
            dispatchers = bot.__dict__.get("dispatchers", [])
            tasks = bot.__dict__.get("tasks", [])

            await update_pooling(new_token, bots, dispatchers, tasks)
            await message.answer("Токен успешно добавлен, и бот запущен!")
        else:
            await message.answer("Токен не может быть пустым.")

@accept_handler.message(Command(commands=['start']))
async def asd(message: Message):
    await message.answer("Привет! Я бот.", parse_mode=ParseMode.HTML)

@accept_handler.message(Command(commands=['addlink']))
async def add_link_handler(message: Message, bot: Bot):
    await func_link_handler(message, bot)

    @accept_handler.message()
    async def handle_user_message(msg: Message, bot: Bot):
        await func_user_message(msg, bot)

@accept_handler.chat_member()
async def handle_bot_added(update: types.ChatMemberUpdated, bot:Bot):
    await func_bot_add(update, bot)

@accept_handler.chat_join_request()
async def handle_join_request(join_request: ChatJoinRequest, bot: Bot):
    await func_join_request(join_request, bot)

@accept_handler.callback_query(lambda c: c.data.startswith("confirm"))
async def handle_confirm_request(callback: CallbackQuery):
    await func_confirm_request(callback)

