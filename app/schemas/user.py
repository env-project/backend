# app/schemas/user.py
import uuid
from typing import Optional

from sqlmodel import SQLModel

from .profile import ProfileDetailRead


class UserCreate(SQLModel):
    email: str
    password: str
    nickname: str


class UserRead(SQLModel):
    id: uuid.UUID
    email: str
    nickname: str


class UserReadWithProfile(UserRead):
    profile: Optional[ProfileDetailRead] = None
