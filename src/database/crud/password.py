from sqlalchemy import insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from depends import Depends, inject

from database.models.password import Password, password as password_model
from utils import get_async_session


@inject
async def insert_new_password(password_data: Password, session: AsyncSession = Depends(get_async_session)) -> None:
    stmt = insert(password_model).values(**password_data.dict())
    await session.execute(stmt)
    await session.commit()


@inject
async def delete_password(group_id: int, service_name: str, encrypt_login: str,
                          session: AsyncSession = Depends(get_async_session)) -> None:
    print(group_id, service_name, encrypt_login)
    stmt = delete(password_model).filter(password_model.c.group_id == group_id).\
        filter(password_model.c.service_name == service_name).\
        filter(password_model.c.encrypt_login == encrypt_login)
    await session.execute(stmt)
    await session.commit()
