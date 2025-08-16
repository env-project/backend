# app/api/v1/endpoints/user.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.core.database import get_async_session
from app.models.user import User
from app.schemas.profile import ProfileDetailRead, ProfileUpdate
from app.schemas.user import UserCreate, UserRead, UserReadWithProfile
from app.services.profile_service import profile_service
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
async def read_users_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    현재 로그인된 사용자의 정보를 가져옵니다.
    """
    profile_data = None
    if current_user.profile:
        recent_posts = await profile_service.get_recent_posts(
            db=db, user_id=current_user.id
        )
        recent_comments = await profile_service.get_recent_comments(
            db=db, user_id=current_user.id
        )

        profile_data = ProfileDetailRead(
            nickname=current_user.nickname,
            image_url=current_user.profile.image_url,
            is_public=current_user.profile.is_public,
            is_bookmarked=False,
            regions=current_user.profile.regions,
            positions=current_user.profile.positions,
            genres=current_user.profile.genres,
            recent_posts=recent_posts,
            recent_comments=recent_comments,
        )

    return UserReadWithProfile(
        id=current_user.id,
        email=current_user.email,
        nickname=current_user.nickname,
        profile=profile_data,
    )


# 내 프로필 수정
@router.patch("/me/profile", response_model=ProfileDetailRead)
async def update_my_profile(
    profile_update: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    현재 로그인된 사용자의 프로필을 수정
    """
    updated_profile = await user_service.update_profile(
        db=db, user=current_user, profile_update=profile_update
    )
    return updated_profile
