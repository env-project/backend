import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ENUM
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: uuid.UUID = Field(primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    email: Optional[str] = Field(max_length=255, unique=True, index=True)
    password_hash: Optional[str] = Field(default=None)
    nickname: str = Field(max_length=20, unique=True, index=True)
    is_active: bool = Field(default=True)
    last_login_at: Optional[datetime] = Field(default=None)
    login_type: str = Field(
        sa_column=Column(
            ENUM("email", "social", name="login_type_enum", create_type=False),
            nullable=False,
        )
    )
