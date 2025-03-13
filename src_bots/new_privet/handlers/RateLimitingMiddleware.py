from abc import ABC

from aiogram import types
from aiogram import BaseMiddleware
import time
from typing import Callable, Any, Awaitable
class RateLimitingMiddleware(BaseMiddleware):
    def __init__(self, limit_interval: float = 2.5):
        super().__init__()
        self.limit_interval = limit_interval
        self.user_last_request_time = {}

    async def __call__(
        self,
        handler: Callable[[types.Update, dict[str, Any]], Awaitable[Any]],
        event: types.Update,
        data: dict[str, Any]
    ) -> Any:
        user_id = None
        if isinstance(event, types.Message):
            user_id = event.from_user.id
        elif isinstance(event, types.CallbackQuery):
            user_id = event.from_user.id

        if user_id:
            current_time = time.time()
            last_request_time = self.user_last_request_time.get(user_id, 0)

            if current_time - last_request_time < self.limit_interval:
                if isinstance(event, types.Message):
                    await event.answer("Слишком много запросов. Пожалуйста, подождите.")
                elif isinstance(event, types.CallbackQuery):
                    await event.answer("Слишком много запросов. Пожалуйста, подождите.", show_alert=True)
                return  # Прерываем обработку

            # Только после успешного выполнения обновляем тайминг
            result = await handler(event, data)
            self.user_last_request_time[user_id] = time.time()
            return result