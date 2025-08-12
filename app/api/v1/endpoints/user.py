# app/api/v1/endpoints/user.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.core.database import get_async_session
from app.models.user import User
from app.schemas.user import ProfileRead, UserCreate, UserRead, UserReadWithProfile
from app.services.user_service import user_service

router = APIRouter()


@router.post("/", response_model=UserRead, status_code=201)
async def create_user(
    user_create: UserCreate, db: AsyncSession = Depends(get_async_session)
):
    created_user = await user_service.create_user(db=db, user_create=user_create)
    return created_user


# 내 정보 조회
@router.get("/me", response_model=UserReadWithProfile)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    현재 로그인된 사용자의 정보를 가져옴
    """
    return current_user


# 프로필 수정 (지금은 비어있는 상태, 뼈대만)
@router.patch("/me/profile", response_model=ProfileRead)
async def update_my_profile(
    # profile_update: ProfileUpdate,
    # current_user: User = Depends(get_current_user),
    # db: AsyncSession = Depends(get_async_session)
):
    """
    현재 로그인된 사용자의 프로필을 수정
    (TODO: 서비스 로직 구현 필요)
    """
    pass  # 우선은 비워둠
