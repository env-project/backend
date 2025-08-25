# app/api/v1/endpoints/user.py
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user, get_current_user_required
from app.core.database import get_async_session
from app.core.security import verify_password
from app.exceptions.exceptions import (
    UserAlreadyBookmarked,
    UserBookmarkNotFound,
    UserNotFound,
)
from app.models.user_model import User
from app.schemas.profile import ProfileDetailRead, ProfileUpdate
from app.schemas.user import UserCreate, UserDelete, UserRead, UserReadWithProfile
from app.services.bookmark_service import BookmarkService, get_bookmark_service
from app.services.user_service import user_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=UserRead, status_code=201)
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

        profile_data = ProfileDetailRead(
            email=current_user.email,
            nickname=current_user.nickname,
            image_url=current_user.profile.image_url,
            is_public=current_user.profile.is_public,
            is_bookmarked=False,
            regions=current_user.profile.regions,
            positions=current_user.profile.positions,
            genres=current_user.profile.genres,
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

    # Optional 필드 안전하게 반환
    return ProfileDetailRead(
        email=current_user.email or None,
        nickname=current_user.nickname or None,
        image_url=updated_profile.image_url or None,
        is_public=(
            updated_profile.is_public
            if updated_profile.is_public is not None
            else False
        ),
        is_bookmarked=False,
        regions=updated_profile.regions or [],
        positions=updated_profile.positions or [],
        genres=updated_profile.genres or [],
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_me(
    user_delete: UserDelete,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    현재 로그인된 사용자의 계정을 영구적으로 삭제
    """
    # 소셜 로그인 사용자는 비밀번호가 없으므로 예외 처리 필요
    if not current_user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="소셜 로그인 사용자는 비밀번호로 계정을 삭제할 수 없습니다.",
        )

    if not verify_password(user_delete.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="잘못된 비밀번호입니다.",
        )

    await user_service.delete_user(db=db, user=current_user)


"""
Bookmark
"""


@router.post(
    "/{user_id}/bookmark",
    summary="타 사용자 북마크 추가(FR-022)",
    description="""
    Responses

    성공
    - HTTP_201_CREATED: 추가 성공
    - HTTP_204_NO_CONTENT: 삭제 성공

    실패
    - HTTP_401_UNAUTHORIZED:
        - Bearer token이 없는 경우(로그인 안되어 있는 경우)
        - 토큰이 만료되었거나
        - 유효하지 않은 토큰 형식일 경우

    - HTTP_400_BAD_REQUEST:
        - 추가: 북마크가 이미 된 사용자일 때
        - 제거: 북마크가 된 사용자가 아닐 때

    - HTTP_404_NOT_FOUND:
        - 북마크할 사용자가 존재하지 않을 때

    - HTTP_422_UNPROCESSABLE_ENTITY(FastAPI server에서 자동 응답):
        - json type이 잘못되었을 때
        - 쿼리 파라미터 지정 데이터타입이 아니거나, 지정된 제약조건에 벗어났을 때

    - HTTP_500_INTERNAL_SERVER_ERROR:
        - 예상치 못한 서버 오류(DB 연결 오류, 타입 에러 등 버그)
    """,
    status_code=status.HTTP_201_CREATED,
)
async def api_add_user_bookmark(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user_required),
    bookmark_service: BookmarkService = Depends(get_bookmark_service),
):
    try:
        await bookmark_service.service_add_user_bookmark(
            current_user_id=current_user.id, target_user_id=user_id
        )
    except UserNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UserAlreadyBookmarked as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error in api_change_is_closed_status: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버에 예상치 못한 오류가 발생했습니다.",
        )


@router.delete(
    "/{user_id}/bookmark",
    summary="타 사용자 북마크 제거(FR-024)",
    description="ref) FR-022",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def apie_remove_user_bookmark(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user_required),
    bookmark_service: BookmarkService = Depends(get_bookmark_service),
):
    try:
        await bookmark_service.service_remove_user_bookmark(current_user.id, user_id)
    except UserNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UserBookmarkNotFound as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error in api_change_is_closed_status: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버에 예상치 못한 오류가 발생했습니다.",
        )
