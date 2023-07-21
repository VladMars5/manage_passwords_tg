from typing import Tuple, Union

from aiogram import Router
from aiogram.filters import Text
from aiogram.types import CallbackQuery, Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.handlers import CallbackQueryHandler
from aiogram.fsm.context import FSMContext
from depends import inject, Depends
from loguru import logger
from asyncpg.exceptions import UniqueViolationError

from keyboards.keyboards import create_dynamic_keyboard, main_menu
from states.group import CreateGroup, UpdateGroup
from utils import check_telegram_profile_message
from database.models.group import Group, UpdateGroupModel
from database.crud.group import insert_new_group, get_groups_by_user, delete_group_by_name, get_group_by_name,\
    update_group_by_name
from filters import CheckBlockUserMiddleware

router = Router()
router.message.middleware(CheckBlockUserMiddleware())


@router.message(Text(text='Создать новую группу'))
async def press_button_create_group(message: Message, state: FSMContext) -> None:
    await state.set_state(CreateGroup.name)
    await message.answer("Введите название группы", reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Отмена")]],
            resize_keyboard=True,
        ),)


@router.message(CreateGroup.name)
async def input_name_group(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(CreateGroup.description)
    await message.answer(
        f"Введите описание группы (Опционально)",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Пропустить")],
                [KeyboardButton(text="Отмена")]
            ],
            resize_keyboard=True,
        ),
    )


@router.message(CreateGroup.description, Text(text="Пропустить"))
async def no_input_description_group(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    data.update({'user_id': message.from_user.id})
    await state.clear()
    answer = ''
    try:
        try:
            group_model = Group(**data)
            del group_model.id
        except Exception as ex:
            logger.error(ex)
            answer = 'Ошибка валидации данных группы!'
            return

        try:
            await insert_new_group(group_data=group_model)
            answer = 'Добавлена новая группа'
        except UniqueViolationError:
            logger.error('Нарушена уникальность названия группы и принадлежности к юзеру')
            answer = 'Группа с таким именем уже существует'
        except Exception as ex:
            logger.error(ex)
            answer = str(ex)
    finally:
        await message.answer(answer, reply_markup=ReplyKeyboardRemove())


@router.message(CreateGroup.description)
async def input_description_group(message: Message, state: FSMContext) -> None:
    data = await state.update_data(description=message.text)
    await state.clear()
    data.update({'user_id': message.from_user.id})
    answer = ''
    try:
        try:
            print(data)
            group_model = Group(**data)
            del group_model.id
        except Exception as ex:
            logger.error(ex)
            answer = 'Ошибка валидации данных группы!'
            return

        try:
            await insert_new_group(group_data=group_model)
            answer = 'Добавлена новая группа'
        except UniqueViolationError:
            logger.error('Нарушена уникальность названия группы и принадлежности к юзеру')
            answer = 'Группа с таким именем уже существует'
        except Exception as ex:
            logger.error(ex)
            answer = str(ex)
    finally:
        await message.reply(answer, reply_markup=ReplyKeyboardRemove())


@router.message(Text(text='delete_group_passwords'))
async def button_delete_group(message: Message) -> None:
    groups_name = await get_groups_by_user(profile_id=message.from_user.id)
    if not groups_name:
        await message.answer('У вас пока что нет созданных групп. Сначала создайте группу!',
                             reply_markup=main_menu)
        return
    # создание динамической клавиатуры и отправка отдельного сообщения с клавиатурой взамен предыдущего состояния
    groups_name = [(group_name, f'delete_group_{group_name}',) for group_name in groups_name]
    buttons = create_dynamic_keyboard(data_buttons=groups_name)
    await message.edit_text('Выберите группу для удаления', reply_markup=buttons.as_markup())


@router.callback_query(Text(startswith="delete_group_"))
async def delete_group_by_name_handler(message: CallbackQuery) -> None:
    name_group = str(message.data).replace('delete_group_', '')
    try:
        await delete_group_by_name(name_group=name_group, profile_id=message.from_user.id)
        answer = f'Группа {name_group} удалена'
    except Exception as ex:
        logger.error(ex)
        answer = str(ex)
    await message.answer(answer, show_alert=True)


@router.callback_query(Text(text='update_group'))
@inject
async def button_delete_group(message: CallbackQueryHandler,
                              user: Tuple[int, Union[str, None]] = Depends(check_telegram_profile_message)) -> None:
    if user[1] is not None:
        await message.message.answer(user[1])
        return

    groups_name = await get_groups_by_user(profile_id=user[0])
    if not groups_name:
        await message.message.answer('У вас пока что нет созданных групп. Сначала создайте группу!',
                                     reply_markup=ReplyKeyboardRemove())
        return
    # создание динамической клавиатуры и отправка отдельного сообщения с клавиатурой взамен предыдущего состояния
    groups_name = [(group_name, f'update_group_{group_name}',) for group_name in groups_name]
    buttons = create_dynamic_keyboard(data_buttons=groups_name)
    await message.message.edit_text('Выберите группу для обновления', reply_markup=buttons.as_markup())


@router.callback_query(Text(startswith="update_group_"))
@inject
async def update_data_group_handler(message: CallbackQuery, state: FSMContext,
                                    user: Tuple[int, Union[str, None]] = Depends(check_telegram_profile_message)) \
        -> None:
    if user[1] is not None:
        await message.message.answer(user[1])
        return
    name_group = str(message.data).replace('update_group_', '')
    await state.set_state(UpdateGroup.old_name)
    await state.update_data(old_name=name_group)
    await state.set_state(UpdateGroup.name)
    await message.message.answer("Введите новое название группы", reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Пропустить")],
                          [KeyboardButton(text="Отмена")]],
                resize_keyboard=True))


@router.message(UpdateGroup.name, Text(text="Пропустить"))
async def skip_update_name_group(message: Message, state: FSMContext) -> None:
    await state.set_state(UpdateGroup.description)
    await message.answer("Введите новое описание группы", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Пропустить")],
                  [KeyboardButton(text="Отмена")]],
        resize_keyboard=True))


@router.message(UpdateGroup.name)
async def update_name_group(message: Message, state: FSMContext) -> None:
    answer, reply_markup = '', None
    try:
        group = await get_group_by_name(name_group=message.text, profile_id=message.from_user.id)
        if not group:
            await state.update_data(name=message.text)
            await state.set_state(UpdateGroup.description)
            answer, reply_markup = 'Введите новое описание группы', ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Пропустить")],
                          [KeyboardButton(text="Отмена")]],
                resize_keyboard=True)
        else:
            answer, reply_markup = 'Группа с таким именем уже существует. Введите другое имя', ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Пропустить")],
                          [KeyboardButton(text="Отмена")]],
                resize_keyboard=True)
    except Exception as ex:
        answer, reply_markup = str(ex), ReplyKeyboardRemove()
    finally:
        await message.answer(answer, reply_markup=reply_markup)


@router.message(UpdateGroup.description, Text(text="Пропустить"))
async def skip_update_description_group(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    old_name, answer = data.get('old_name'), ''
    try:
        try:
            update_group_model = UpdateGroupModel(**data)
        except Exception as ex:
            logger.error(ex)
            answer = 'Ошибка валидации данных'
            return

        try:
            await update_group_by_name(name_group=old_name, profile_id=message.from_user.id,
                                       group_data=update_group_model)
            answer = 'Данные группы обновлены'
        except Exception as ex:
            logger.error(ex)
            answer = str(ex)
    finally:
        await message.answer(answer, reply_markup=ReplyKeyboardRemove())


@router.message(UpdateGroup.description)
async def input_description_group(message: Message, state: FSMContext) -> None:
    data = await state.update_data(description=message.text)
    await state.clear()
    old_name, answer = data.get('old_name'), ''
    try:
        try:
            update_group_model = UpdateGroupModel(**data)
        except Exception as ex:
            logger.error(ex)
            answer = 'Ошибка валидации данных'
            return

        try:
            await update_group_by_name(name_group=old_name, profile_id=message.from_user.id,
                                       group_data=update_group_model)
            answer = 'Данные группы обновлены'
        except Exception as ex:
            logger.error(ex)
            answer = str(ex)
    finally:
        await message.answer(answer, reply_markup=ReplyKeyboardRemove())


@router.callback_query(Text(text='get_passwords_by_group'))
@inject
async def get_passwords_by_group_user(message: CallbackQueryHandler,
                                      user: Tuple[int, Union[str, None]] = Depends(check_telegram_profile_message)) \
        -> None:
    if user[1] is not None:
        await message.message.answer(user[1])
        return

    groups_name = await get_groups_by_user(profile_id=user[0])
    if not groups_name:
        await message.message.answer('У вас пока что нет созданных групп. Сначала создайте группу!',
                                     reply_markup=ReplyKeyboardRemove())
        return
    # создание динамической клавиатуры и отправка отдельного сообщения с клавиатурой взамен предыдущего состояния
    groups_name = [(group_name, f'get_passwords_{group_name}',) for group_name in groups_name]
    buttons = create_dynamic_keyboard(data_buttons=groups_name)
    await message.message.edit_text('Выберите группу для просмотра паролей', reply_markup=buttons.as_markup())


# @router.callback_query(Text(startswith="get_passwords_"))
# async def get_passwords_by_group(callback_query: CallbackQuery) -> None:
#     получить пароли логины
#     расшифровать
#     отдать в читаемой форме
#     print(callback_query)
#     # отправить отдельное сообщение и потом удалить его и форму кнопок
#     sent_message = await callback_query.message.answer('Здесь будут выводится пароли группы')
#     await asyncio.sleep(5)
#     await sent_message.delete()

# TODO: show
