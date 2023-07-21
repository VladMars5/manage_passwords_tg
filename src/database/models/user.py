from sqlalchemy import Boolean, Column, Integer, String, Table
from database.database import metadata

user = Table(
    "user",
    metadata,
    Column("id", Integer, nullable=False, primary_key=True),
    Column("username", String(length=256)),
    Column("is_block", Boolean, server_default='false', nullable=False),
    Column("is_admin", Boolean, server_default='false', nullable=False),
)
