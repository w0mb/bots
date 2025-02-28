from abc import ABC, abstractmethod

class IBotFactory(ABC):
    @abstractmethod
    async def create_bot(self, token: str):
        pass

    @abstractmethod
    async def start_polling(self, bot, dp):
        pass