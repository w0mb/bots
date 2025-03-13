# import asyncio
# import logging
# from typing import List
# from aiogram import Bot
# from aiogram import Dispatcher
#
# class GracefulShutdown:
#     def __init__(self, bots: List[Bot], dispatchers: List[Dispatcher]):
#         self.bots = bots
#         self.dispatchers = dispatchers
#
#     async def shutdown(self):
#         """Корректное завершение работы."""
#         logging.info("Завершение работы...")
#         for bot, dp in zip(self.bots, self.dispatchers):
#             await self.stop_bot(bot, dp)
#         tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
#         for task in tasks:
#             task.cancel()
#         await asyncio.gather(*tasks, return_exceptions=True)
#
#     async def stop_bot(self, bot: Bot, dp: Dispatcher):
#         """Остановка одного бота."""
#         try:
#             await dp.stop_polling()
#             await bot.session.close()
#             logging.info(f"Бот с токеном {bot.token} остановлен.")
#         except Exception as e:
#             logging.error(f"Ошибка при остановке бота: {e}")