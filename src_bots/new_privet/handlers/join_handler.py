import asyncio
import logging
import aiogram
from aiogram import Bot

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ChatJoinRequest, CallbackQuery, Message
from aiogram.filters import Command

from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from src_bots.new_privet.handlers.helpers.join_funcs import (
    is_user_member, pic_spam, spam, approve, check_subscriptions
)

from src_bots.new_privet.handlers.base_handler import BaseHandler
from src_bots.new_privet.keybords.keyboard_manager import KeyboardManager

class JoinHandler(BaseHandler):
    def __init__(self, keyboard_manager: KeyboardManager | None):
        super().__init__()
        self.join_request_data = {}
        self.keyboard_manager = keyboard_manager
        self.sleep_time = 3600
        self.spam_type = "both"
        self.wait_for_approve = 600
        self.send_count1 = 5
        self.send_count2 = 5
        self.approve_count = -1

        class Form(StatesGroup):
            add_sleep = State()
            add_spam_type = State()
            add_wait_for_approve = State()

        @self.router.message(Command(commands=["addsleep"]))
        async def add_sleep_handler(msg: Message, bot: Bot, state: FSMContext):
            await msg.answer("введите количество секунд задержки перед отправкой спам-сообщения\n"
                             "по умолчанию задержка = 1 часу\n"
                             "!это команда перезаписывает значение задержки!\n"
                             "т.е. если у вас была установлена задержка 100000сек и вы вызываете команду снова, передавая в нее значение 1сек\n"
                             "тогда задержка будет равна новому значению 1сек")
            await state.set_state(Form.add_sleep)

            @self.router.message(Form.add_sleep)
            async def add_sleep(msg: Message):
                self.sleep_time = int(msg.text)
                await state.clear()

        @self.router.message(Command(commands=["spamtype"]))
        async def spam_type_handler(msg: Message, bot: Bot, state: FSMContext):
            await msg.answer("выбери тип спама\n"
                             "both - оба варианта(картинка с кнопками и текст с ссылкой)\n"
                             "only_text - только текст с ссылкой\n"
                             "only_pic - картинка с кнопками, в которых ссылки\n"
                             "выбор типа также перезаписывает предыдущее состояние, по умолчанию стоит вариант both\n"
                             "сообщения будут отправлять по 5 раз")
            await state.set_state(Form.add_spam_type)
            @self.router.message(Form.add_spam_type)
            async def spam_type(msg: Message):
                self.spam_type = msg.text
                await state.clear()

        @self.router.message(Command(commands=["approvesleep"]))
        async def approve_cleep_handler(msg: Message, bot: Bot, state: FSMContext):
            await msg.answer("напиши сколько боту ждать в секундах прежде чем впустить пользователя в канал,\n"
                             "когда пользователь нажимает 'Подтвердить' на клавитуре\n"
                             "1 час = 3600 сек.\n"
                             "по умолчанию стоит 1000 сек\n"
                             "ввод данных перезаписывает предыдущее значение")
            await state.set_state(Form.add_wait_for_approve)
            @self.router.message(Form.add_wait_for_approve)
            async def approve_cleepo(msg: Message):
                self.wait_for_approve = int(msg.text)
                await state.clear()

        @self.router.chat_join_request()
        async def handle_join_request(join_request: ChatJoinRequest, bot: Bot):
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger(__name__)
            user_id = join_request.from_user.id
            channel_id = join_request.chat.id
            bot_info = await bot.get_me()
            logger.info(f"Обработка заявки от пользователя {user_id} для канала {channel_id}")

            file_path = f"src_bots/new_privet/bot_channel_ids/{bot.id}.txt"
            logger.info(f"Путь к файлу настроек: {file_path}")

            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    logger.info("Файл настроек успешно открыт")
                    lines = file.readlines()
                    for line in lines:
                        parts = line.strip().split(":")
                        if len(parts) >= 4 and parts[0] == str(channel_id):
                            accept_immediately = parts[3].lower() == "true"
                            logger.info(f"Найдено значение accept_immediately: {accept_immediately}")
                            break
                    else:
                        accept_immediately = True
                        logger.info("Канал не найден, используем значение по умолчанию: True")
            except FileNotFoundError:
                logger.error(f"Файл не найден: {file_path}")
                accept_immediately = True

            if accept_immediately:
                logger.info("Принимаем заявку сразу")
                await approve(bot, user_id, channel_id)
            else:
                logger.info("Заявка не принимается сразу, ожидаем подписки на другие каналы")

                self.join_request_data[user_id] = channel_id

                logging.basicConfig(level=logging.INFO)
                logger = logging.getLogger(__name__)
                # Запускаем pic_spam асинхронно
                async def send_pic_spam():
                    for i in range(1, self.send_count1 + 1):
                        if not await is_user_member(bot, user_id, channel_id):
                            try:
                                bot_info = await bot.get_me()
                                bot_id = bot_info.id
                                kb = await keyboard_manager.get_keyboard(bot_id)
                                await pic_spam(bot, user_id, str(i), kb.get_keyboard())
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
                        await asyncio.sleep(self.sleep_time)

                async def send_text_spam():
                    for i in range(1, self.send_count2 + 1):
                        if not await is_user_member(bot, user_id, channel_id):
                            try:
                                await spam(bot, user_id)
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
                        await asyncio.sleep(self.sleep_time)

                async def run_spam():
                    if self.spam_type == "both":
                        await send_pic_spam()  # Сначала выполняем pic_spam
                        await send_text_spam()  # Затем выполняем text_spam
                    elif self.spam_type == "only_text":
                        await send_text_spam()
                    elif self.spam_type == "only_pic":
                        await send_pic_spam()

                # Запускаем спам в фоновом режиме
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
                with open(f"src_bots/new_privet/keybords/{bot_info.id}.txt", "r", encoding="utf-8") as file:
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