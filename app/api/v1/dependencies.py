# app/api/v1/dependencies.py
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.core.config import settings
from app.core.database import get_async_session
from app.models.user_model import Profile, User
from app.schemas.token import TokenPayload

# /api/v1/auth/token 경로에서 토큰을 가져오도록 설정
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user(
    db: AsyncSession = Depends(get_async_session), token: str = Depends(reusable_oauth2)
) -> User:
    """
    JWT 토큰을 검증 및 현재 로그인된 사용자 객체를 반환
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # User를 조회할 때, profile 관계를 즉시 로딩(eager load)하도록 옵션을 추가
    statement = (
        select(User)
        .options(
            selectinload(User.profile).selectinload(Profile.regions),
            selectinload(User.profile).selectinload(Profile.positions),
            selectinload(User.profile).selectinload(Profile.genres),
        )
        .where(User.id == token_data.sub)
    )
    result = await db.execute(statement)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# 토큰이 있으면 사용자 객체,
# 없거나, 토큰이 유효하지 않으면 None
optional_oauth2 = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


async def get_current_user_or_none(
    db: AsyncSession = Depends(get_async_session),
    token: Optional[str] = Depends(optional_oauth2),
) -> Optional[User]:

    if not token:
        return None

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    statement = select(User).where(User.id == token_data.sub)
    result = await db.execute(statement)
    return result.scalar_one_or_none()


async def get_current_required(
    db: AsyncSession = Depends(get_async_session),
    token: str = Depends(reusable_oauth2),
) -> User:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    statement = select(User).where(User.id == token_data.sub)
    result = await db.execute(statement)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
