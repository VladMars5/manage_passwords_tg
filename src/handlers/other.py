from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message()
async def unknown_message(message: Message) -> None:
    await message.reply("Я не понимаю ваше сообщение! Пожалуйста обратитесь к документации /help")
