from aiogram import types, Bot

from handlers.base_handler import BaseHandler
from handlers.helpers.join_funcs import update_channel_file
from handlers.helpers.public_join_funcs import public_update_channel_file

class BotAddToChannelHandler(BaseHandler):
    def __init__(self):
        super().__init__()


        @self.router.my_chat_member()
        async def handle_bot_added(update: types.ChatMemberUpdated, bot: Bot):
            chat = update.chat
            new_status = update.new_chat_member.status
            if not chat.username:
                await update_channel_file(str(chat.id), chat.title, new_status, bot)
            else:
                await public_update_channel_file(str(chat.id), chat.title, new_status, bot)