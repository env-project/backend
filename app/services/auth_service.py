# app/services/auth_service.py
from datetime import datetime, timedelta, timezone
from typing import Any, Union

from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.config import settings
from app.models.user_model import RefreshToken, User
from app.schemas.token import Token, TokenPayload


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

    async def get_user_from_refresh_token(
        self, db: AsyncSession, token: str
    ) -> User | None:
        """리프레시 토큰을 검증하고 사용자 객체를 반환합니다."""
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            token_data = TokenPayload(**payload)
        except (jwt.JWTError, ValidationError):
            return None

        statement = select(RefreshToken).where(RefreshToken.jti == token_data.sub)
        result = await db.execute(statement)
        refresh_token_obj = result.scalar_one_or_none()

        if not refresh_token_obj or refresh_token_obj.is_revoked:
            return None

        user_statement = select(User).where(User.id == refresh_token_obj.user_id)
        user_result = await db.execute(user_statement)
        return user_result.scalar_one_or_none()

    async def revoke_refresh_token(self, db: AsyncSession, token: str):
        """리프레시 토큰을 DB에서 찾아 is_revoked를 True로 설정"""
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            token_data = TokenPayload(**payload)
        except (jwt.JWTError, ValidationError):
            # 유효하지 않은 토큰은 이미 무효화된 것과 같으므로 그냥 넘어감
            return

        statement = select(RefreshToken).where(RefreshToken.jti == token_data.sub)
        result = await db.execute(statement)
        refresh_token_obj = result.scalar_one_or_none()

        if refresh_token_obj:
            refresh_token_obj.is_revoked = True
            db.add(refresh_token_obj)
            await db.commit()


auth_service = AuthService()
