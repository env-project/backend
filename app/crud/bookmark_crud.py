# app/crud/bookmark_crud.py - 수정된 버전

import uuid

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import PostBookmark, RecruitingPost, User, UserBookmark


async def get_user_bookmark_by_id(
    db: AsyncSession, current_user_id: uuid.UUID, target_user_id: uuid.UUID
) -> PostBookmark | None:
    """
    id로 userbookmark를 조회합니다.
    """
    stmt = select(UserBookmark).where(
        UserBookmark.user_id == current_user_id,
        UserBookmark.bookmarked_user_id == target_user_id,
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# FR-022: 타 사용자 북마크 추가
async def add_user_bookmark(
    db: AsyncSession, current_user_id: uuid.UUID, target_user: User
) -> None:
    bookmarked_user_id = target_user.id

    user_bookmark = UserBookmark(
        user_id=current_user_id, bookmarked_user_id=bookmarked_user_id
    )

    target_user.bookmark_count += 1
    db.add(user_bookmark)
    await db.commit()


# FR-024: 타 사용자 북마크 제거
async def delete_user_bookmark(
    db: AsyncSession, current_user_id: uuid.UUID, target_user: User
) -> None:
    bookmarked_user_id = target_user.id

    stmt = delete(UserBookmark).where(
        UserBookmark.user_id == current_user_id,
        UserBookmark.bookmarked_user_id == bookmarked_user_id,
    )

    target_user.bookmark_count -= 1
    await db.execute(stmt)
    await db.commit()


# 북마크 카운트 업데이트
# async def update_bookmark_count(
#     db: AsyncSession, target_user_id: uuid.UUID, increment: bool
# ) -> None:
#     # 현재 북마크 수 조회
#     count_stmt = select(func.count(UserBookmark.id)).where(
#         UserBookmark.bookmarked_user_id == target_user_id
#     )
#     result = await db.execute(count_stmt)
#     current_count = result.scalar() or 0
#
#     # 모든 북마크의 카운트 업데이트
#     bookmarks_stmt = select(UserBookmark).where(
#         UserBookmark.bookmarked_user_id == target_user_id
#     )
#     bookmarks_result = await db.execute(bookmarks_stmt)
#     bookmarks = bookmarks_result.scalars().all()
#
#     for bookmark in bookmarks:
#         bookmark.bookmark_count = current_count
#
#     await db.commit()


async def get_post_bookmark_by_id(
    db: AsyncSession, current_user_id: uuid.UUID, post_id: uuid.UUID
) -> PostBookmark | None:
    """
    id로 postbookmark를 조회합니다.
    """
    stmt = select(PostBookmark).where(
        PostBookmark.user_id == current_user_id,
        PostBookmark.bookmarked_post_id == post_id,
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# FR-022: 구인글 북마크 추가
async def add_post_bookmark(
    db: AsyncSession, current_user_id: uuid.UUID, post: RecruitingPost
) -> None:
    bookmarked_post_id = post.id

    post_bookmark = PostBookmark(
        user_id=current_user_id, bookmarked_post_id=bookmarked_post_id
    )

    # postcode_stmt = select(func.count(PostBookmark.id)).where(PostBookmark.bookmarked_post_id == bookmarked_post_id)
    post.bookmarks_count += 1

    db.add(post_bookmark)
    await db.commit()


# FR-024: 구인글 북마크 제거
async def delete_post_bookmark(
    db: AsyncSession, current_user_id: uuid.UUID, post: RecruitingPost
) -> None:
    bookmarked_post_id = post.id

    stmt = delete(PostBookmark).where(
        PostBookmark.user_id == current_user_id,
        PostBookmark.bookmarked_post_id == bookmarked_post_id,
    )

    post.bookmarks_count -= 1
    await db.execute(stmt)
    await db.commit()
