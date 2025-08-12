# app/schemas/user.py
import uuid

from sqlmodel import SQLModel


# 회원가입 시 Request
class UserCreate(SQLModel):
    email: str
    password: str
    nickname: str


# 회원가입 후 Response
class UserRead(SQLModel):
    id: uuid.UUID
    email: str
    nickname: str
