# app/crud/bookmark_crud.py

import uuid
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import UserBookmark, PostBookmark


# FR-022: 타 사용자 북마크 추가(POST)
async def create_user_bookmark(
    db: AsyncSession,
    user_id: uuid.UUID,
    target_user_id: uuid.UUID) -> None:
    bookmark = UserBookmark(user_id=user_id, target_user_id=target_user_id)
    db.add(bookmark)
    await db.commit()


# FR-024: 타 사용자 북마크 제거(DELETE)
async def delete_user_bookmark(
    db: AsyncSession,
    user_id: uuid.UUID,
    target_user_id: uuid.UUID) -> None:
    stmt = delete(UserBookmark).where(
        UserBookmark.user_id == user_id,
        UserBookmark.target_user_id == target_user_id,
    )
    await db.execute(stmt)
    await db.commit()

# FR-022: 구인글 북마크 추가(POST)
async def create_post_bookmark(
    db: AsyncSession,
    user_id: uuid.UUID,
    post_id: uuid.UUID) -> None:
    bookmark = PostBookmark(user_id=user_id, post_id=post_id)
    db.add(bookmark)
    await db.commit()


# FR-024: 구인글 북마크 제거(DELETE)
async def delete_post_bookmark(
    db: AsyncSession,
    user_id: uuid.UUID,
    post_id: uuid.UUID) -> None:
    stmt = delete(PostBookmark).where(
        PostBookmark.user_id == user_id,
        PostBookmark.post_id == post_id,
    )
    await db.execute(stmt)
    await db.commit()
