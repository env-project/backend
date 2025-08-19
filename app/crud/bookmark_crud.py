# app/crud/bookmark_crud.py - 수정된 버전

import uuid

from sqlalchemy import delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import PostBookmark, UserBookmark


# FR-022: 타 사용자 북마크 추가(POST)
async def create_user_bookmark(
    db: AsyncSession, user_id: uuid.UUID, bookmarked_user_id: uuid.UUID
) -> UserBookmark:
    bookmark = UserBookmark(user_id=user_id, bookmarked_user_id=bookmarked_user_id)
    db.add(bookmark)
    await db.commit()
    await db.refresh(bookmark)
    return bookmark


# FR-024: 타 사용자 북마크 제거(DELETE)
async def delete_user_bookmark(
    db: AsyncSession, user_id: uuid.UUID, bookmarked_user_id: uuid.UUID
) -> None:
    stmt = delete(UserBookmark).where(
        UserBookmark.user_id == user_id,
        UserBookmark.bookmarked_user_id == bookmarked_user_id,
    )
    await db.execute(stmt)
    await db.commit()


# 북마크 카운트 업데이트
async def update_bookmark_count(
    db: AsyncSession, target_user_id: uuid.UUID, increment: bool
) -> None:
    # 현재 북마크 수 조회
    count_stmt = select(func.count(UserBookmark.id)).where(
        UserBookmark.bookmarked_user_id == target_user_id
    )
    result = await db.execute(count_stmt)
    current_count = result.scalar() or 0

    # 모든 북마크의 카운트 업데이트
    bookmarks_stmt = select(UserBookmark).where(
        UserBookmark.bookmarked_user_id == target_user_id
    )
    bookmarks_result = await db.execute(bookmarks_stmt)
    bookmarks = bookmarks_result.scalars().all()

    for bookmark in bookmarks:
        bookmark.bookmark_count = current_count

    await db.commit()


# FR-022: 구인글 북마크 추가(POST)
async def create_post_bookmark(
    db: AsyncSession, user_id: uuid.UUID, bookmarked_post_id: uuid.UUID
) -> PostBookmark:
    bookmark = PostBookmark(user_id=user_id, bookmarked_post_id=bookmarked_post_id)
    db.add(bookmark)
    await db.commit()
    await db.refresh(bookmark)
    return bookmark


# FR-024: 구인글 북마크 제거(DELETE)
async def delete_post_bookmark(
    db: AsyncSession, user_id: uuid.UUID, bookmarked_post_id: uuid.UUID
) -> None:
    stmt = delete(PostBookmark).where(
        PostBookmark.user_id == user_id,
        PostBookmark.bookmarked_post_id == bookmarked_post_id,
    )
    await db.execute(stmt)
    await db.commit()
