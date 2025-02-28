import os
from idlelib.undo import Command
import logging
from aiogram import Router, types, Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ChatJoinRequest, ChatInviteLink, CallbackQuery, Message
from aiogram.filters import Command
import asyncio
import random

from src_bots.privet.captionTexts import text1, text_send1, text_send2
from src_bots.privet.inline_kb import Keyboard

# =================== Глобальный словарь для хранения данных ===================
join_request_data = {}
keyboards = {}
channel_ids_filename = "chaneel_ids.txt"
# =================== Router ===================
handler_router = Router()

# =================== Функции ===================




    # Запись обновленных данных в файл
    with open(channel_ids_filename, "w", encoding="utf-8") as file:
        for file_chat_id, (file_title, file_bot_id) in channel_dict.items():
            # Используем существующий bot_id, если канал не изменялся
            current_bot_id = bot_id if file_chat_id == chat_id else file_bot_id
            file.write(f"{file_chat_id}:{file_title}:{current_bot_id}\n")




async def get_chat_id_from_file():
    with open(channel_ids_filename, "r") as file:
        return [int(line.split(":")[0]) for line in file]







async def members_count_from_file(bot: Bot):
    """Возвращает количество участников в каждом канале, в которых состоит бот"""
    chat_ids = await get_chat_id_from_file()
    members_count_list = []
    bot_info = await bot.get_me()
    bot_id = bot_info.id  # Получаем ID бота

    for chat_id in chat_ids:
        if await is_user_member(bot, bot_id, chat_id):  # Дожидаемся результата проверки
            members_count = await bot.get_chat_member_count(chat_id)
            members_count_list.append({"members_count": members_count, "chat_id": chat_id})

    return members_count_list


async def get_min_members_count(members_count_list: list[dict]) -> dict:
    """Возвращает канал с минимальным количеством участников"""
    return min(members_count_list, key=lambda x: x['members_count'])


async def generate_invite_link(bot: Bot, members_count_list) -> str:
    """Создаёт ссылку-приглашение в канал с наименьшим количеством участников и сохраняет её в файл."""
    file_path = "links.txt"
    min_chat = await get_min_members_count(members_count_list)
    chat_id = str(min_chat["chat_id"])

    with open(file_path, "r", encoding="utf-8") as file:
        if os.path.getsize(file_path) != 0:
            for line in file:
                saved_link, saved_chat_id,_ = line.strip().split(";")
                if saved_chat_id == chat_id:
                    return saved_link
    invite_link = await bot.create_chat_invite_link(
        chat_id=chat_id,
        name="Приглашение от бота",
        expire_date=None,
        member_limit=None,
        creates_join_request=True
    )

    with open(file_path, "a", encoding="utf-8") as file:
        bot_info = await bot.get_me()
        file.write(f"{invite_link.invite_link};{chat_id};{bot_info.id}\n")

    return invite_link.invite_link





async def send_welcome_message(bot: Bot, chat_id: int, user_id: int):
    """Отправляет приветственное сообщение новому участнику."""
    send_count1 = 5
    send_count2 = 5
    member = await bot.get_chat_member(chat_id, user_id)
    if member.status in ['member', 'administrator', 'creator']:
        for i in range(1, send_count1 + 1):
            await pic_spam(bot, user_id, str(i))
            await asyncio.sleep(15)
        for i in range(1, send_count2 + 1):
            await spam(bot, user_id)
            await asyncio.sleep(15)

    # @router.my_chat_member()
    # async def handle_member_status(update: types.ChatMemberUpdated, bot: Bot):
    #     new_status = update.new_chat_member.status
    #     user_id = update.new_chat_member.user.id
    #     channel_id = join_request_data.get(user_id)
    #     # Если пользователь стал участником канала
    #     if new_status == "member":
    #         await send_welcome_message(bot, channel_id, user_id)




# =================== Хэндлеры ===================
def create_router():
    router = Router()



    return router

