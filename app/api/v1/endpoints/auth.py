# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.database import get_async_session
from app.core.security import verify_password
from app.models.user_model import User
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
    # 이메일(username 필드 사용)로 사용자를 찾고
    statement = select(User).where(User.email == form_data.username)
    result = await db.execute(statement)
    print("결과:", result)
    user = result.scalar_one_or_none()

    # 이메일이 틀리면
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="이메일이 존재하지 않습니다.",
        )

    # 비밀번호가 틀리면
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="비밀번호를 확인해주세요.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 토큰을 생성하여 반환
    return auth_service.create_tokens(user=user)
