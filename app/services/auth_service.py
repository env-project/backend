# app/services/auth_service.py
from datetime import datetime, timedelta, timezone
from typing import Any, Union

from jose import jwt

from app.core.config import settings
from app.models.user import User
from app.schemas.token import Token


class AuthService:
    def create_access_token(
        self, subject: Union[str, Any], expires_delta: timedelta | None = None
    ) -> str:
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode = {"exp": expire, "sub": str(subject)}
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    def create_refresh_token(
        self, subject: Union[str, Any], expires_delta: timedelta | None = None
    ) -> str:
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )

        to_encode = {"exp": expire, "sub": str(subject)}
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    def create_tokens(self, user: User) -> Token:
        access_token = self.create_access_token(subject=user.id)
        refresh_token = self.create_refresh_token(subject=user.id)
        return Token(access_token=access_token, refresh_token=refresh_token)


auth_service = AuthService()
