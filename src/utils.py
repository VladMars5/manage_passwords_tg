from typing import Union, Tuple
import secrets

from aiogram.types import Message, CallbackQuery
from aiogram.handlers import CallbackQueryHandler
from depends import Depends, inject
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
import logging
from cryptography.fernet import Fernet

from database.database import get_async_session
from database.models.user import user as user_model
from config import ENCRYPTION_KEY_LOGIN, ENCRYPTION_KEY_PASSWORD, alphabet_password

cipher_suite_login = Fernet(ENCRYPTION_KEY_LOGIN)
cipher_suite_password = Fernet(ENCRYPTION_KEY_PASSWORD)


@inject
async def check_telegram_profile_message(message: Union[Message, CallbackQuery, CallbackQueryHandler],
                                         session: AsyncSession = Depends(get_async_session)) \
        -> Tuple[int, Union[str, None]]:
    profile_id, error = int(message.from_user.id), None
    query = select(user_model).where(user_model.c.id == profile_id)
    user = await session.execute(query)
    user = user.fetchone()
    if not user:
        stmt = insert(user_model).values(id=profile_id, username=message.from_user.username)
        try:
            await session.execute(stmt)
            await session.commit()
        except Exception as ex:
            logging.error(ex)
            error = str(ex)
    else:
        if user.is_block is True:
            error = f'User by profile_id -> {user.id} and username -> {user.username} is block!'
    return profile_id, error


def encrypt_str(original_str: str, is_password: bool = False) -> str:
    encrypt_origin = original_str.encode('utf-8')
    encrypted_str = cipher_suite_password.encrypt(encrypt_origin).decode('utf-8') if is_password \
        else cipher_suite_login.encrypt(encrypt_origin).decode('utf-8')
    return encrypted_str


def decrypt_str(encrypted_str: str, is_password: bool = False) -> str:
    decrypted_str = cipher_suite_password.decrypt(encrypted_str.encode('utf-8')) if is_password \
        else cipher_suite_login.decrypt(encrypted_str.encode('utf-8'))
    decrypted_str = decrypted_str.decode('utf-8')
    return decrypted_str


def generate_password(length_password: int = 12) -> str:
    length_password = length_password if length_password > 30 else length_password
    return ''.join([secrets.choice(alphabet_password) for _ in range(length_password)])
