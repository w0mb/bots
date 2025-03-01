from abc import ABC, abstractmethod

class IBotFactory(ABC):
    @abstractmethod
    async def create_bot(self, token: str):
        pass

    @abstractmethod
    async def start_polling(self, bot, dp):
        pass

    @abstractmethod
    async def stop_pooling(self, bot, dp):
        pass
    @abstractmethod
    async def get_dispatcher_by_bot(self, bot):
        pass
    @abstractmethod
    async def get_bot_by_username(self, username):
        pass
    @abstractmethod
    async def get_all_pooling_bots(self):
        pass
