from typing import Optional

from sqlalchemy import Column, Integer, String, Table, Identity, ForeignKey
from database.database import metadata
from pydantic import BaseModel, validator, root_validator

group = Table(
    "group",
    metadata,
    Column("id", Integer, Identity(), nullable=False, unique=True),
    Column("name", String(length=256), nullable=False, primary_key=True),
    Column("description", String(length=2048)),
    Column("user_id", Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False, primary_key=True)
)


class Group(BaseModel):
    id: Optional[int]
    name: str
    description: Optional[str]
    user_id: int

    @validator('name')
    def validate_name_len(cls, v):
        if len(v) > 256:
            raise ValueError('Name should not be more than 256 characters')
        return v

    @validator('description')
    def validate_name_description(cls, v):
        if v and len(v) > 2048:
            raise ValueError('Description should not be more than 2048 characters')
        return v


class UpdateGroupModel(BaseModel):
    name: Optional[str]
    description: Optional[str]

    @root_validator
    def check_all_empty_values(cls, values):
        if not any(values.values()):
            raise ValueError('At least one field must be filled in to update')
        if values.get('name') and len(values.get('name')) > 256:
            raise ValueError('Name should not be more than 256 characters')
        if values.get('description') and len(values.get('description')) > 2048:
            raise ValueError('Description should not be more than 2048 characters')
        return values
