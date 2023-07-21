from sqlalchemy import Column, String, Table, Identity, ForeignKey, BigInteger
from pydantic import BaseModel, validator

from database.database import metadata

password = Table(
    "password",
    metadata,
    Column("id", BigInteger, Identity(), nullable=False, unique=True),
    Column("service_name", String(length=512), nullable=False, primary_key=True),
    Column("encrypt_login", String(length=1024), nullable=False, primary_key=True),
    Column("encrypt_password", String(length=2048), nullable=False),
    Column("group_id", BigInteger, ForeignKey('group.id', ondelete='CASCADE'), nullable=False, primary_key=True)
)


class Password(BaseModel):
    service_name: str
    encrypt_login: str
    encrypt_password: str
    group_id: int

    @validator('service_name')
    def validate_name_len(cls, v):
        if len(v) > 512:
            raise ValueError('ServiceName should not be more than 512 characters')
        return v

    @validator('encrypt_login')
    def validate_encrypt_login(cls, v):
        if v and len(v) > 1024:
            raise ValueError('EncryptLogin should not be more than 1024 characters')
        return v

    @validator('encrypt_password')
    def validate_encrypt_password(cls, v):
        if v and len(v) > 2048:
            raise ValueError('EncryptPassword should not be more than 2048 characters')
        return v


# class UpdateGroupModel(BaseModel):
#     name: Optional[str]
#     description: Optional[str]
#
#     @root_validator
#     def check_all_empty_values(cls, values):
#         if not any(values.values()):
#             raise ValueError('At least one field must be filled in to update')
#         if values.get('name') and len(values.get('name')) > 256:
#             raise ValueError('Name should not be more than 256 characters')
#         if values.get('description') and len(values.get('description')) > 2048:
#             raise ValueError('Description should not be more than 2048 characters')
#         return values
