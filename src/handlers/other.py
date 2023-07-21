from typing import Tuple, Union

from aiogram import Router
from aiogram.types import Message
from depends import Depends, inject

from utils import check_telegram_profile_message

router = Router()


@router.message()
@inject
async def unknown_message(message: Message,
                          user: Tuple[int, Union[str, None]] = Depends(check_telegram_profile_message)) -> None:
    if user[1] is not None:
        await message.answer(user[1])
        return
    await message.reply("Я не понимаю ваше сообщение! Пожалуйста обратитесь к документации /help")
