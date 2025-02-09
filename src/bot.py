from aiogram import Router, F
from aiogram.types import Message

router_message = Router()

@router_message.message(F.text)
async def message_with_text(message: Message):
    await message.answer("Это текстовое сообщение!")