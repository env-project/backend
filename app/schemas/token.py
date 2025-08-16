# app/schemas/token.py
from typing import Optional

from sqlmodel import SQLModel


class Token(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: Optional[str] = None  # sub는 토큰의 주체(subject) - (user_id)
