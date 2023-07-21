from typing import Tuple, Union

from aiogram import Router
from aiogram.filters import Command, Text
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
import logging
from depends import Depends, inject

from keyboards.keyboards import main_menu
from utils import check_telegram_profile_message

router = Router()


@router.message(Command(commands=['start']))
@inject
async def start_command(message: Message, user: Tuple[int, Union[str, None]] = Depends(check_telegram_profile_message))\
        -> None:
    if user[1] is not None:
        await message.answer(user[1])
        return
    await message.answer(f"Привет User({user[0]})! Это Бот менеджер паролей!", reply_markup=main_menu)


@router.message(Command(commands=['help']))
@inject
async def help_command(message: Message, user: Tuple[int, Union[str, None]] = Depends(check_telegram_profile_message))\
        -> None:
    if user[1] is not None:
        await message.answer(user[1])
        return
    # TODO: добавить описание команд бота
    await message.reply("Описание команд ...")


@router.message(Command(commands=['cancel']))
@router.message(Text(text="отмена"))
@router.message(Text(text="Отмена"))
@router.message(Text(text="cancel"))
@router.message(Text(text="Cancel"))
@inject
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is not None:
        logging.info(f"Отмена состояния {current_state}")
        await state.clear()
    await message.answer(
        "Действие отменено",
        reply_markup=ReplyKeyboardRemove()
        )
