# app/api/v1/bookmark_router.py

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# DB 세션 의존성
from app.core.database import get_async_session

# 인증된 사용자 정보 가져오기
# app.core.auth는 추가되면 주석 해제할 것
# get_current_user 관련 오류는 모두 auth 문제이므로 당장은 무시합니다
# from app.core.auth import get_current_user
from app.models.user_model import User

# 북마크 서비스
from app.services.bookmark_service import BookmarkService

# 응답 스키마
from app.schemas.bookmark_schema import BookmarkResponse

bookmark_router = APIRouter()


# BookmarkService 인스턴스를 의존성으로 주입
def get_bookmark_service(
    session: AsyncSession = Depends(get_async_session),
) -> BookmarkService:
    return BookmarkService(session)


# 타 사용자 북마크 추가
@bookmark_router.post(
    "/{user_id}/bookmark",
    response_model=BookmarkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="사용자 북마크 추가",
    description="현재 로그인한 사용자가 다른 사용자를 북마크합니다.",
)
async def add_user_bookmark(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    bookmark_service: BookmarkService = Depends(get_bookmark_service),
):
    try:
        return await bookmark_service.add_user_bookmark(current_user.id, user_id)
    except Exception:
        raise HTTPException(status_code=500, detail="BOOKMARK_ADD_ERROR")


# 타 사용자 북마크 제거
@bookmark_router.delete(
    "/{user_id}/bookmark",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="사용자 북마크 제거",
    description="현재 로그인한 사용자가 북마크한 사용자를 제거합니다.",
)
async def remove_user_bookmark(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    bookmark_service: BookmarkService = Depends(get_bookmark_service),
):
    try:
        await bookmark_service.remove_user_bookmark(current_user.id, user_id)
    except Exception:
        raise HTTPException(status_code=500, detail="BOOKMARK_REMOVE_ERROR")


# 구인글 북마크 추가
@bookmark_router.post(
    "/{post_id}/bookmark",
    response_model=BookmarkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="구인글 북마크 추가",
    description="현재 로그인한 사용자가 구인글을 북마크합니다.",
)
async def add_post_bookmark(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    bookmark_service: BookmarkService = Depends(get_bookmark_service),
):
    try:
        return await bookmark_service.add_post_bookmark(current_user.id, post_id)
    except Exception:
        raise HTTPException(status_code=500, detail="BOOKMARK_ADD_ERROR")


# 구인글 북마크 제거
@bookmark_router.delete(
    "/{post_id}/bookmark",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="구인글 북마크 제거",
    description="현재 로그인한 사용자가 북마크한 구인글을 제거합니다.",
)
async def remove_post_bookmark(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    bookmark_service: BookmarkService = Depends(get_bookmark_service),
):
    try:
        await bookmark_service.remove_post_bookmark(current_user.id, post_id)
    except Exception:
        raise HTTPException(status_code=500, detail="BOOKMARK_REMOVE_ERROR")
