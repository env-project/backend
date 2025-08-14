# app/services/bookmark_service.py

import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.bookmark_crud import (
    create_user_bookmark,
    delete_user_bookmark,
    create_post_bookmark,
    delete_post_bookmark,
    get_user_bookmark,
    get_post_bookmark,
)
from app.exceptions.exceptions import BookmarkNotFound
from app.schemas.bookmark_schema import BookmarkResponse


# 타 사용자 북마크 추가
async def service_create_user_bookmark(
    db: AsyncSession,
    current_user_id: uuid.UUID,
    target_user_id: uuid.UUID,
) -> BookmarkResponse:
    await create_user_bookmark(db, current_user_id, target_user_id)
    return BookmarkResponse(message=f"User {target_user_id} bookmarked by {current_user_id}")


# 타 사용자 북마크 제거
async def service_delete_user_bookmark(
    db: AsyncSession,
    current_user_id: uuid.UUID,
    target_user_id: uuid.UUID,
) -> BookmarkResponse:
    bookmark = await get_user_bookmark(db, current_user_id, target_user_id)
    if not bookmark:
        raise BookmarkNotFound()

    await delete_user_bookmark(db, current_user_id, target_user_id)
    return BookmarkResponse(message=f"User {target_user_id} unbookmarked by {current_user_id}")


# 구인글 북마크 추가
async def service_create_post_bookmark(
    db: AsyncSession,
    current_user_id: uuid.UUID,
    post_id: uuid.UUID,
) -> BookmarkResponse:
    await create_post_bookmark(db, current_user_id, post_id)
    return BookmarkResponse(message=f"Post {post_id} bookmarked by {current_user_id}")


# 구인글 북마크 제거
async def service_delete_post_bookmark(
    db: AsyncSession,
    current_user_id: uuid.UUID,
    post_id: uuid.UUID,
) -> BookmarkResponse:
    bookmark = await get_post_bookmark(db, current_user_id, post_id)
    if not bookmark:
        raise BookmarkNotFound()

    await delete_post_bookmark(db, current_user_id, post_id)
    return BookmarkResponse(message=f"Post {post_id} unbookmarked by {current_user_id}")
