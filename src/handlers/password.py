import asyncio
from typing import Tuple, Union

from aiogram import Router
from aiogram.filters import Text
from aiogram.types import CallbackQuery, Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.handlers import CallbackQueryHandler
from aiogram.fsm.context import FSMContext
from depends import inject, Depends
from loguru import logger

from keyboards.keyboards import create_dynamic_keyboard
from states.password import CreatePassword, DeletePassword
from utils import check_telegram_profile_message, encrypt_str, generate_password
from database.crud.group import get_groups_by_user, get_group_by_name, get_group_id_by_name
from database.crud.password import insert_new_password, delete_password
from database.models.password import Password

router = Router()


@router.callback_query(Text(text='create_new_password'))
@inject
async def press_button_create_password(message: CallbackQueryHandler,
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
    groups_name = [(group_name, f'create_password_{group_name}',) for group_name in groups_name]
    buttons = create_dynamic_keyboard(data_buttons=groups_name)
    await message.message.edit_text('Выберите группу для нового пароля', reply_markup=buttons.as_markup())


@router.callback_query(Text(startswith="create_password_"))
@inject
async def create_password_group_handler(message: CallbackQuery, state: FSMContext,
                                        user: Tuple[int, Union[str, None]] = Depends(check_telegram_profile_message)) \
        -> None:
    if user[1] is not None:
        await message.message.answer(user[1])
        return
    answer, reply_markup = '', None
    try:
        name_group = str(message.data).replace('create_password_', '')
        groups = await get_group_by_name(name_group=name_group, profile_id=user[0])
        group_id = [group.id for group in groups]
        if not group_id:
            answer, reply_markup = 'Нет группы с таким именем. Попробуйте еще раз', ReplyKeyboardRemove()
        else:
            await state.set_state(CreatePassword.group_id)
            await state.update_data(group_id=group_id[0])
            await state.set_state(CreatePassword.service_name)
            answer = "Введите название сервиса от которого пароль"
            reply_markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Отмена")]],
                                               resize_keyboard=True)
    except Exception as ex:
        answer, reply_markup = str(ex), ReplyKeyboardRemove()
    finally:
        await message.message.answer(answer, reply_markup=reply_markup)


@router.message(CreatePassword.service_name)
async def input_service_name_password(message: Message, state: FSMContext) -> None:
    await state.update_data(service_name=message.text)
    await state.set_state(CreatePassword.login)
    await message.answer("Введите логин",
                         reply_markup=ReplyKeyboardMarkup(
                             keyboard=[[KeyboardButton(text="Отмена")]],
                             resize_keyboard=True))


@router.message(CreatePassword.login)
async def input_login_password(message: Message, state: FSMContext) -> None:
    await state.update_data(login=message.text)
    await state.set_state(CreatePassword.password)
    await message.answer("Введите пароль",
                         reply_markup=ReplyKeyboardMarkup(
                             keyboard=[[KeyboardButton(text="Сгенерировать пароль")],
                                       [KeyboardButton(text="Отмена")]],
                             resize_keyboard=True))
    await asyncio.sleep(10)
    await message.delete()


@router.message(CreatePassword.password, Text(text="Сгенерировать пароль"))
async def input_password_generate(message: Message, state: FSMContext) -> None:
    data = await state.update_data(password=message.text)
    await state.clear()

    data.update({'encrypt_login': encrypt_str(original_str=data.get('login'))})
    gen_password = generate_password()
    send_message = await message.answer(gen_password, reply_markup=ReplyKeyboardRemove())
    data.update({'encrypt_password': encrypt_str(original_str=gen_password, is_password=True)})
    answer = ''
    try:
        try:
            password_data = Password(**data)
        except Exception as ex:
            logger.error(ex)
            answer = 'Ошибка валидации данных'
            return
        try:
            await insert_new_password(password_data=password_data)
            answer = 'Записан новый пароль'
        except Exception as ex:
            logger.error(ex)
            answer = str(ex)
    finally:
        await message.answer(answer, reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(10)
    await send_message.delete()


@router.message(CreatePassword.password)
async def input_password(message: Message, state: FSMContext) -> None:
    data = await state.update_data(password=message.text)
    await state.clear()

    data.update({'encrypt_login': encrypt_str(original_str=data.get('login'))})
    data.update({'encrypt_password': encrypt_str(original_str=data.get('password'), is_password=True)})
    answer = ''
    try:
        try:
            password_data = Password(**data)
        except Exception as ex:
            logger.error(ex)
            answer = 'Ошибка валидации данных'
            return
        try:
            await insert_new_password(password_data=password_data)
            answer = 'Записан новый пароль'
        except Exception as ex:
            logger.error(ex)
            answer = str(ex)
    finally:
        await message.answer(answer, reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(10)
    await message.delete()


@router.callback_query(Text(text='delete_pass_button'))
@inject
async def button_delete_password(message: CallbackQueryHandler,
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
    groups_name = [(group_name, f'delete_password_{group_name}',) for group_name in groups_name]
    buttons = create_dynamic_keyboard(data_buttons=groups_name)
    await message.message.edit_text('Выберите группу из которой удалить пароль', reply_markup=buttons.as_markup())


@router.callback_query(Text(startswith="delete_password_"))
@inject
async def delete_group_by_name_handler(message: CallbackQuery, state: FSMContext,
                                       user: Tuple[int, Union[str, None]] = Depends(check_telegram_profile_message)) \
        -> None:
    if user[1] is not None:
        await message.message.answer(user[1])
        return
    name_group = str(message.data).replace('delete_password_', '')
    group_id = await get_group_id_by_name(name_group=name_group, profile_id=user[0])
    if not group_id:
        await state.clear()
        await message.message.answer('Нет группы с таким именем.')
        return

    await state.set_state(DeletePassword.group_id)
    await state.update_data(group_id=group_id)
    await state.set_state(DeletePassword.service_name)
    await message.message.answer("Введите название сервиса от которого пароль",
                                 reply_markup=ReplyKeyboardMarkup(
                                     keyboard=[[KeyboardButton(text="Отмена")]],
                                     resize_keyboard=True))


@router.message(DeletePassword.service_name)
async def delete_service_name_password(message: Message, state: FSMContext) -> None:
    await state.update_data(service_name=message.text)
    await state.set_state(DeletePassword.login)
    await message.answer("Введите логин",
                         reply_markup=ReplyKeyboardMarkup(
                             keyboard=[[KeyboardButton(text="Отмена")]],
                             resize_keyboard=True))


@router.message(DeletePassword.login)
async def delete_login_password(message: Message, state: FSMContext) -> None:
    data = await state.update_data(login=message.text)
    await state.clear()
    answer, reply_markup = '', None
    try:
        print(data.get('login'))
        login = data.get('login')
        data1 = encrypt_str(original_str=login)
        from utils import decrypt_str
        print(decrypt_str(data1))
        print(login)
        print(data.get('login'))
        await delete_password(group_id=data.get('group_id'), service_name=data.get('service_name'),
                              encrypt_login=encrypt_str(original_str=data.get('login')))
        answer, reply_markup = 'Пароль успешно удален', ReplyKeyboardRemove()
    except Exception as ex:
        logger.error(ex)
        answer, reply_markup = str(ex), ReplyKeyboardRemove()
    finally:
        await message.answer(answer, reply_markup=reply_markup)
    await asyncio.sleep(10)
    await message.delete()


@router.callback_query(Text(text='update_pass_button'))
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


# @router.callback_query(Text(startswith="update_group_"))
# @inject
# async def update_data_group_handler(message: CallbackQuery, state: FSMContext,
#                                     user: Tuple[int, Union[str, None]] = Depends(check_telegram_profile_message)) \
#         -> None:
#     if user[1] is not None:
#         await message.message.answer(user[1])
#         return
#     name_group = str(message.data).replace('update_group_', '')
#     await state.set_state(UpdateGroup.old_name)
#     await state.update_data(old_name=name_group)
#     await state.set_state(UpdateGroup.name)
#     await message.message.answer("Введите новое название группы", reply_markup=ReplyKeyboardMarkup(
#                 keyboard=[[KeyboardButton(text="Пропустить")],
#                           [KeyboardButton(text="Отмена")]],
#                 resize_keyboard=True))
#
#
# @router.message(UpdateGroup.name, Text(text="Пропустить"))
# async def skip_update_name_group(message: Message, state: FSMContext) -> None:
#     await state.set_state(UpdateGroup.description)
#     await message.answer("Введите новое описание группы", reply_markup=ReplyKeyboardMarkup(
#         keyboard=[[KeyboardButton(text="Пропустить")],
#                   [KeyboardButton(text="Отмена")]],
#         resize_keyboard=True))
#
#
# @router.message(UpdateGroup.name)
# async def update_name_group(message: Message, state: FSMContext) -> None:
#     answer, reply_markup = '', None
#     try:
#         group = await get_group_by_name(name_group=message.text, profile_id=message.from_user.id)
#         if not group:
#             await state.update_data(name=message.text)
#             await state.set_state(UpdateGroup.description)
#             answer, reply_markup = 'Введите новое описание группы', ReplyKeyboardMarkup(
#                 keyboard=[[KeyboardButton(text="Пропустить")],
#                           [KeyboardButton(text="Отмена")]],
#                 resize_keyboard=True)
#         else:
#             answer, reply_markup = 'Группа с таким именем уже существует. Введите другое имя', ReplyKeyboardMarkup(
#                 keyboard=[[KeyboardButton(text="Пропустить")],
#                           [KeyboardButton(text="Отмена")]],
#                 resize_keyboard=True)
#     except Exception as ex:
#         answer, reply_markup = str(ex), ReplyKeyboardRemove()
#     finally:
#         await message.answer(answer, reply_markup=reply_markup)
#
#
# @router.message(UpdateGroup.description, Text(text="Пропустить"))
# async def skip_update_description_group(message: Message, state: FSMContext) -> None:
#     data = await state.get_data()
#     await state.clear()
#     old_name, answer = data.get('old_name'), ''
#     try:
#         try:
#             update_group_model = UpdateGroupModel(**data)
#         except Exception as ex:
#             logger.error(ex)
#             answer = 'Ошибка валидации данных'
#             return
#
#         try:
#             await update_group_by_name(name_group=old_name, profile_id=message.from_user.id,
#                                        group_data=update_group_model)
#             answer = 'Данные группы обновлены'
#         except Exception as ex:
#             logger.error(ex)
#             answer = str(ex)
#     finally:
#         await message.answer(answer, reply_markup=ReplyKeyboardRemove())
#
#
# @router.message(UpdateGroup.description)
# async def input_description_group(message: Message, state: FSMContext) -> None:
#     data = await state.update_data(description=message.text)
#     await state.clear()
#     old_name, answer = data.get('old_name'), ''
#     try:
#         try:
#             update_group_model = UpdateGroupModel(**data)
#         except Exception as ex:
#             logger.error(ex)
#             answer = 'Ошибка валидации данных'
#             return
#
#         try:
#             await update_group_by_name(name_group=old_name, profile_id=message.from_user.id,
#                                        group_data=update_group_model)
#             answer = 'Данные группы обновлены'
#         except Exception as ex:
#             logger.error(ex)
#             answer = str(ex)
#     finally:
#         await message.answer(answer, reply_markup=ReplyKeyboardRemove())
#
#
# @router.callback_query(Text(text='get_passwords_by_group'))
# @inject
# async def get_passwords_by_group_user(message: CallbackQueryHandler,
#                                       user: Tuple[int, Union[str, None]] = Depends(check_telegram_profile_message)) \
#         -> None:
#     if user[1] is not None:
#         await message.message.answer(user[1])
#         return
#
#     groups_name = await get_groups_by_user(profile_id=user[0])
#     if not groups_name:
#         await message.message.answer('У вас пока что нет созданных групп. Сначала создайте группу!',
#                                      reply_markup=ReplyKeyboardRemove())
#         return
#     # создание динамической клавиатуры и отправка отдельного сообщения с клавиатурой взамен предыдущего состояния
#     groups_name = [(group_name, f'get_passwords_{group_name}',) for group_name in groups_name]
#     buttons = create_dynamic_keyboard(data_buttons=groups_name)
#     await message.message.edit_text('Выберите группу для просмотра паролей', reply_markup=buttons.as_markup())
#
#
# # @router.callback_query(Text(startswith="get_passwords_"))
# # async def get_passwords_by_group(callback_query: CallbackQuery) -> None:
# #     получить пароли логины
# #     расшифровать
# #     отдать в читаемой форме
# #     print(callback_query)
# #     # отправить отдельное сообщение и потом удалить его и форму кнопок
# #     sent_message = await callback_query.message.answer('Здесь будут выводится пароли группы')
# #     await asyncio.sleep(5)
# #     await sent_message.delete()
# TODO: search password