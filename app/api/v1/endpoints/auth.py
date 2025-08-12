# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.database import get_async_session
from app.core.security import verify_password
from app.models.user import User
from app.schemas.token import Token
from app.services.auth_service import auth_service

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session),
):
    """
    이메일과 비밀번호로 로그인하여 액세스 토큰을 발급
    """
    # 1. 이메일(username 필드 사용)로 사용자를 찾고
    statement = select(User).where(User.email == form_data.username)
    result = await db.execute(statement)
    user = result.scalar_one_or_none()

    # 2. 사용자가 없거나 비밀번호가 틀리면 에러를 반환
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. 토큰을 생성하여 반환
    return auth_service.create_tokens(user=user)
