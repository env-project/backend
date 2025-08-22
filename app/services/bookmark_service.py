# app/services/bookmark_service.py

import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session

# 북마크 관련 CRUD 함수
from app.crud.bookmark_crud import (
    add_post_bookmark,
    create_user_bookmark,
    delete_post_bookmark,
    delete_user_bookmark,
    get_post_bookmark_by_id,
    update_bookmark_count,
)
from app.crud.recruiting_crud import get_recruiting_by_id
from app.exceptions.exceptions import (
    PostAlreadyBookmarked,
    PostBookmarkNotFound,
    PostNotFound,
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

    # FR-022: 구인글 북마크 추가
    async def service_add_post_bookmark(
        self, current_user_id: uuid.UUID, post_id: uuid.UUID
    ) -> None:  # BookmarkResponse:
        post = await get_recruiting_by_id(self.db, post_id)
        if not post:
            raise PostNotFound()

        bookmark = await get_post_bookmark_by_id(self.db, current_user_id, post_id)
        if bookmark:
            raise PostAlreadyBookmarked()

        await add_post_bookmark(self.db, current_user_id, post)
        # return BookmarkResponse(
        #     id=post_bookmark.id,
        #     message=f"Post {post_id} bookmarked by {current_user_id}",
        #     created_at=post_bookmark.created_at,
        # )

    # FR-024: 구인글 북마크 제거
    async def service_remove_post_bookmark(
        self, current_user_id: uuid.UUID, post_id: uuid.UUID
    ) -> None:
        post = await get_recruiting_by_id(self.db, post_id)
        if not post:
            raise PostNotFound()

        bookmark = await get_post_bookmark_by_id(self.db, current_user_id, post_id)
        if not bookmark:
            raise PostBookmarkNotFound()

        await delete_post_bookmark(self.db, current_user_id, post)


# BookmarkService 인스턴스를 의존성으로 주입
def get_bookmark_service(
    session: AsyncSession = Depends(get_async_session),
) -> BookmarkService:
    return BookmarkService(session)
