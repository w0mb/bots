from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
import asyncio
import time

class RateLimitingMiddleware(BaseMiddleware):
    def __init__(self, limit_interval: float = 2.5):
        self.limit_interval = limit_interval
        self.user_last_request_time = {}
        super().__init__()

    async def on_pre_process_message(self, message: types.Message, data: dict):
        user_id = message.from_user.id
        current_time = time.time()

        if user_id in self.user_last_request_time:
            last_request_time = self.user_last_request_time[user_id]
            if current_time - last_request_time < self.limit_interval:
                await message.answer("Слишком много запросов. Пожалуйста, подождите.")
                raise CancelHandler()  # Отменяем обработку текущего запроса

        self.user_last_request_time[user_id] = current_time

    async def on_pre_process_callback_query(self, callback_query: types.CallbackQuery, data: dict):
        user_id = callback_query.from_user.id
        current_time = time.time()

        if user_id in self.user_last_request_time:
            last_request_time = self.user_last_request_time[user_id]
            if current_time - last_request_time < self.limit_interval:
                await callback_query.answer("Слишком много запросов. Пожалуйста, подождите.", show_alert=True)
                raise CancelHandler()  # Отменяем обработку текущего запроса

        self.user_last_request_time[user_id] = current_time