# app/api/v1/endpoints/user.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session  # 비동기 세션을 가져옴
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import user_service

router = APIRouter()


@router.post("/", response_model=UserRead, status_code=201)
# [수정] 함수를 반드시 'async def'로 정의해야 합니다.
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_async_session)):
    """
    새로운 사용자를 생성합니다 (이메일 회원가입).
    """
    # [수정] 비동기 함수를 호출하므로 'await'를 사용해야 합니다.
    created_user = await user_service.create_user(db=db, user_create=user)
    return created_user
