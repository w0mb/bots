import asyncio
import logging
import os

import aiogram
from aiogram import Bot

from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ChatJoinRequest, CallbackQuery, \
    FSInputFile

from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.helpers.join_funcs import (
    is_user_member, pic_spam, spam, approve, check_subscriptions, get_accept_type, send_creo_spam,
)

from handlers.base_handler import BaseHandler
from interface_bot_factory import IBotFactory
from keybords import keyboard_manager
from keybords.keyboard_manager import KeyboardManager
from utils.file_utils import get_strings_from_file


class JoinHandler(BaseHandler):
    def __init__(self, keyboard_manager: KeyboardManager | None, bot_factory: IBotFactory | None):
        super().__init__()
        self.bot_factory = bot_factory
        self.join_request_data = {}
        self.keyboard_manager = keyboard_manager
        self.sleep_time = 3600
        self.spam_type = "both"
        self.wait_for_approve = 10
        self.send_count1 = 1
        self.send_count2 = 1
        self.approve_count = -1
        self.video_path = ""
        self.video_caption = ""
        self.creo_but_count = 1
        self.but_text = "Перейти$http://example.com"
        self.urlb = "http://example.com"
        self.vpuskat = 1

    async def initialize(self):
        await self._init_from_settings_file()
    async def _init_from_settings_file(self):
        bot_tokens = await get_strings_from_file("tokens/tokens.txt")
        bot_info_list = []
        bot_ids = []
        for token in bot_tokens:
            bot = Bot(token=token)
            bot_info = await bot.get_me()
            bot_ids.append(bot_info.id)
            await bot.session.close()
        for id in bot_ids:
            file_path = f"settings/{id}.txt"
            if not os.path.exists(file_path):
                print(f"Файл настроек {file_path} не найден. Использую значения по умолчанию.")
                continue  # Продолжаем выполнение для других файлов

            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith("#"):  # Пропускаем пустые строки и комментарии
                        continue

                    try:
                        field_name, value = line.split("#", 1)
                        field_name = field_name.strip()
                        value = value.strip()

                        # Проверяем, существует ли поле в классе
                        if hasattr(self, field_name):
                            current_value = getattr(self, field_name)
                            # Преобразуем значение в нужный тип
                            if isinstance(current_value, int):
                                setattr(self, field_name, int(value))
                            elif isinstance(current_value, str):
                                setattr(self, field_name, value)
                            elif isinstance(current_value, float):
                                setattr(self, field_name, float(value))
                            elif isinstance(current_value, bool):
                                setattr(self, field_name, value.lower() == "true")
                            else:
                                print(f"Поле {field_name} имеет неподдерживаемый тип: {type(current_value)}")
                        else:
                            print(f"Поле {field_name} не найдено в классе. Пропускаю.")
                    except ValueError as e:
                        print(f"Ошибка при обработке строки '{line}': {e}")
                    except Exception as e:
                        print(f"Неизвестная ошибка при обработке строки '{line}': {e}")



        class Form(StatesGroup):
            add_sleep = State()
            add_spam_type = State()
            add_wait_for_approve = State()
            add_vid_cap = State()
            add_video_creo = State()
            add_url_to_buttons_cre = State()
            add_button_text_creo = State()
            add_vpusk = State()

        @self.router.chat_join_request()
        async def handle_join_request(join_request: ChatJoinRequest, bot: Bot):
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger(__name__)
            user_id = join_request.from_user.id
            channel_id = join_request.chat.id
            bot_info = await bot.get_me()
            logger.info(f"Обработка заявки от пользователя {user_id} для канала {channel_id}")

            try:
                accept_immediately = await get_accept_type(bot.id, channel_id)
            except FileNotFoundError:
                logger.error(f"Файл не найден: bot_channel_ids/{bot.id}.txt, accept_immediately = True")
                accept_immediately = True
            if accept_immediately:
                logger.info("Принимаем заявку сразу")
                await asyncio.sleep(3)
                await approve(bot, user_id, channel_id)
            else:
                logger.info("Заявка не принимается сразу, ожидаем подписки на другие каналы")

                self.join_request_data[user_id] = channel_id

                logging.basicConfig(level=logging.INFO)
                logger = logging.getLogger(__name__)



                async def send_pic_spam():
                    for i in range(1, self.send_count1 + 1):
                        if not await is_user_member(bot, user_id, channel_id):
                            try:
                                bot_info = await bot.get_me()
                                bot_id = bot_info.id
                                kb = await keyboard_manager.get_keyboard(bot_id)
                                await pic_spam(bot, user_id, str(i), kb.get_keyboard())
                                await asyncio.sleep(self.sleep_time)
                            except aiogram.exceptions.TelegramForbiddenError as e:
                                # Пользователь заблокировал бота
                                logger.error(f"Пользователь {user_id} заблокировал бота. Остановка отправки сообщений.")
                                break
                            except aiogram.exceptions.TelegramBadRequest as e:
                                # Пользователь уже является участником канала
                                if "user is already a participant" in str(e):
                                    logger.info(f"Пользователь {user_id} уже является участником канала. Остановка отправки сообщений.")
                                    break
                                else:
                                    logger.error(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
                            except Exception as e:
                                # Другие ошибки
                                logger.error(f"Неизвестная ошибка при отправке сообщения пользователю {user_id}: {e}")


                async def send_text_spam():
                    for i in range(1, self.send_count2 + 1):
                        if not await is_user_member(bot, user_id, channel_id):
                            try:
                                await spam(bot, user_id)
                                await asyncio.sleep(self.sleep_time)
                            except TelegramForbiddenError as e:
                                # Пользователь заблокировал бота
                                logger.error(f"Пользователь {user_id} заблокировал бота. Остановка отправки сообщений.")
                                break
                            except TelegramBadRequest as e:
                                # Пользователь уже является участником канала
                                if "user is already a participant" in str(e):
                                    logger.info(f"Пользователь {user_id} уже является участником канала. Остановка отправки сообщений.")
                                    break
                                else:
                                    logger.error(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
                            except Exception as e:
                                # Другие ошибки
                                logger.error(f"Неизвестная ошибка при отправке сообщения пользователю {user_id}: {e}")
                async def run_spam():
                    if self.spam_type == "both":
                        await send_pic_spam()  # Сначала выполняем pic_spam
                        await send_text_spam()  # Затем выполняем text_spam
                    elif self.spam_type == "only_text":
                        await send_text_spam()
                    elif self.spam_type == "only_pic":
                        await send_pic_spam()
                    elif self.spam_type == "creo":
                        await send_creo_spam(bot, user_id, channel_id, self.send_count1, self.sleep_time, self.video_path,
                                             self.video_caption, self.but_text, self.urlb,
                                             self.vpuskat)

                asyncio.create_task(run_spam())

        @self.router.callback_query(lambda c: c.data.startswith("confirm"))
        async def handle_confirm_request(callback: CallbackQuery):
            bot = callback.bot
            user_id = callback.from_user.id
            channel_id = self.join_request_data.get(user_id)

            if channel_id:
                # Получаем список каналов, на которые нужно подписаться
                channels_to_subscribe = []
                bot_info = await bot.get_me()
                file = await get_strings_from_file(f"keybords/{bot_info.id}.txt")
                for line in file:
                    parts = line.strip().split("$")
                    if await is_user_member(bot, bot_info.id, int(parts[2])):
                        channels_to_subscribe.append(int(parts[2]))  # Добавляем channel_id как целое число

                # Проверяем подписки
                if await check_subscriptions(bot, user_id, channels_to_subscribe):
                    await callback.answer("Ваша заявка скоро будет одобрена, пожалуйста ожидайте!")
                    await asyncio.sleep(self.wait_for_approve)
                    await approve(bot, user_id, channel_id)
                    await callback.answer("Ваша заявка одобрена!")
                    self.join_request_data.pop(user_id, None)
                else:
                    await callback.answer("Вы не подписались на все необходимые каналы.")
            else:
                await callback.answer("Ошибка: данные не найдены.")