# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.config import settings
from app.core.database import get_async_session
from app.core.security import verify_password
from app.models.user_model import User
from app.schemas.token import Token
from app.services.auth_service import auth_service

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session),
):
    """
    이메일과 비밀번호로 로그인하여 액세스 토큰 발급 + HttpOnly 쿠키에 refresh_token 저장
    """
    statement = select(User).where(User.email == form_data.username)
    result = await db.execute(statement)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="이메일이 존재하지 않습니다.",
        )

    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="비밀번호를 확인해주세요.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # DB 저장 + 토큰 생성
    tokens = await auth_service.create_tokens_and_save_refresh_token(db=db, user=user)

    # HttpOnly 쿠키에 refresh_token 저장
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  # 초 단위
        path="/",
        secure=False,  # HTTPS 환경에서는 True
        samesite="lax",
    )

    return tokens


@router.post("/token/refresh", response_model=Token)
async def refresh_access_token(
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_async_session),
):
    """
    HttpOnly 쿠키의 refresh_token 사용하여 새로운 access_token 발급 + 쿠키 갱신
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

    # 새 토큰 생성 및 DB 저장
    tokens = await auth_service.create_tokens_and_save_refresh_token(db=db, user=user)

    # 쿠키 갱신
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/",
        secure=False,
        samesite="lax",
    )

    return tokens


@router.delete("/token", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response, request: Request, db: AsyncSession = Depends(get_async_session)
):
    """
    로그아웃: HttpOnly 쿠키 무효화 + DB refresh_token is_revoked 처리
    """
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await auth_service.revoke_refresh_token(db, token=refresh_token)

    # 클라이언트 쿠키 삭제
    response.delete_cookie(key="refresh_token", path="/", httponly=True)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
