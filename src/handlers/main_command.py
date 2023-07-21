import logging

from aiogram import Router
from aiogram.filters import Command, Text
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.keyboards import main_menu
from filters import CheckBlockUserMiddleware

router = Router()
router.message.middleware(CheckBlockUserMiddleware())


@router.message(Command(commands=['start']))
async def start_command(message: Message) -> None:
    await message.answer(f"Привет User({message.from_user.username})! Это Бот менеджер паролей!",
                         reply_markup=main_menu)


@router.message(Command(commands=['help']))
async def help_command(message: Message) -> None:
    # TODO: добавить описание команд бота
    await message.reply("Описание команд ...")


@router.message(Command(commands=['cancel']))
@router.message(Text(text="отмена"))
@router.message(Text(text="Отмена"))
@router.message(Text(text="cancel"))
@router.message(Text(text="Cancel"))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is not None:
        logging.info(f"Отмена состояния {current_state}")
        await state.clear()
    await message.answer(
        "Действие отменено",
        reply_markup=main_menu
        )
