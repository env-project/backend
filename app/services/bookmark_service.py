# app/services/bookmark_service.py

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

# 북마크 관련 CRUD 함수
from app.crud.bookmark_crud import (
    create_post_bookmark,
    create_user_bookmark,
    delete_post_bookmark,
    delete_user_bookmark,
    update_bookmark_count,
)

# 응답 스키마
from app.schemas.bookmark_schema import BookmarkResponse


class BookmarkService:
    def __init__(self, db: AsyncSession):
        # DB 세션을 서비스 인스턴스에 저장
        self.db = db

    async def add_user_bookmark(
        self, current_user_id: uuid.UUID, target_user_id: uuid.UUID
    ) -> BookmarkResponse:
        """
        타 사용자 북마크 추가
        - 북마크 생성 후 대상 유저의 북마크 카운트를 증가시킴
        """
        bookmark = await create_user_bookmark(self.db, current_user_id, target_user_id)
        await update_bookmark_count(self.db, target_user_id, increment=True)
        return BookmarkResponse(
            id=bookmark.id,
            message=f"User {target_user_id} bookmarked by {current_user_id}",
            created_at=bookmark.created_at,
        )

    async def remove_user_bookmark(
        self, current_user_id: uuid.UUID, target_user_id: uuid.UUID
    ) -> None:
        """
        타 사용자 북마크 제거
        - 북마크 삭제 후 대상 유저의 북마크 카운트를 감소시킴
        """
        await delete_user_bookmark(self.db, current_user_id, target_user_id)
        await update_bookmark_count(self.db, target_user_id, increment=False)

    async def add_post_bookmark(
        self, current_user_id: uuid.UUID, post_id: uuid.UUID
    ) -> BookmarkResponse:
        """
        구인글 북마크 추가
        - 북마크 생성
        """
        bookmark = await create_post_bookmark(self.db, current_user_id, post_id)
        return BookmarkResponse(
            id=bookmark.id,
            message=f"Post {post_id} bookmarked by {current_user_id}",
            created_at=bookmark.created_at,
        )

    async def remove_post_bookmark(
        self, current_user_id: uuid.UUID, post_id: uuid.UUID
    ) -> None:
        """
        구인글 북마크 제거
        - 북마크 삭제
        """
        await delete_post_bookmark(self.db, current_user_id, post_id)
