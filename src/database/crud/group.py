from typing import Optional, List

from sqlalchemy import insert, select, delete, and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from depends import Depends, inject

from database.models.group import Group, group as group_model, UpdateGroupModel
from utils import get_async_session


@inject
async def insert_new_group(group_data: Group, session: AsyncSession = Depends(get_async_session)) -> None:
    stmt = insert(group_model).values(**group_data.dict())
    await session.execute(stmt)
    await session.commit()


@inject
async def get_groups_by_user(profile_id: int, session: AsyncSession = Depends(get_async_session)) -> list:
    query = select(group_model.c.name).where(group_model.c.user_id == profile_id)
    groups = await session.execute(query)
    groups = groups.all()
    return [group[0] for group in groups]


@inject
async def delete_group_by_name(name_group: str, profile_id: int,
                               session: AsyncSession = Depends(get_async_session)) -> None:
    stmt = delete(group_model).where(and_(group_model.c.name == name_group, group_model.c.user_id == profile_id))
    await session.execute(stmt)
    await session.commit()


@inject
async def get_group_by_name(name_group: str, profile_id: int,
                            session: AsyncSession = Depends(get_async_session)) -> List[Optional[Group]]:
    stmt = select(group_model).where(and_(group_model.c.name == name_group, group_model.c.user_id == profile_id))
    groups = await session.execute(stmt)
    groups = groups.all()
    return [Group(**group._mapping) for group in groups]


@inject
async def update_group_by_name(name_group: str, profile_id: int, group_data: UpdateGroupModel,
                               session: AsyncSession = Depends(get_async_session)) -> None:
    stmt = update(group_model).where(and_(group_model.c.name == name_group, group_model.c.user_id == profile_id)).\
        values(**group_data.dict())
    await session.execute(stmt)
    await session.commit()


@inject
async def get_group_id_by_name(name_group: str, profile_id: int,
                               session: AsyncSession = Depends(get_async_session)) -> int or None:
    query = select(group_model.c.id).where(and_(group_model.c.name == name_group, group_model.c.user_id == profile_id))
    query = await session.execute(query)
    group_id = query.first()
    return group_id[0] if group_id else None
