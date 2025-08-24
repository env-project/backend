# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
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

    # 토큰을 생성하고 DB에 저장하는 서비스 함수를 호출
    return await auth_service.create_tokens_and_save_refresh_token(db=db, user=user)


@router.post("/token/refresh", response_model=Token)
async def refresh_access_token(
    request: Request, db: AsyncSession = Depends(get_async_session)
):
    """
    HttpOnly 쿠키의 refresh_token을 사용하여 새로운 access_token을 발급
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found in cookies",
        )

    user = await auth_service.get_user_from_refresh_token(db, token=refresh_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    return await auth_service.create_tokens_and_save_refresh_token(db=db, user=user)


@router.delete("/token", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response, request: Request, db: AsyncSession = Depends(get_async_session)
):
    """
    로그아웃. HttpOnly 쿠키의 refresh_token을 무효화
    """
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await auth_service.revoke_refresh_token(db, token=refresh_token)

    # 클라이언트의 쿠키를 삭제하도록 응답 헤더를 설정
    response.delete_cookie(key="refresh_token", path="/api/v1/auth", httponly=True)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
