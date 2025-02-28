from aiogram import Router

class BaseHandler:
    def __init__(self):
        self.router = Router()

    def get_router(self):
        """
        Возвращает роутер.
        """
        return self.router