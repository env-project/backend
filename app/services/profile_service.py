# app/services/profile_service.py
import uuid
from typing import List, Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import col, select

from app.models.bookmark_model import UserBookmark
from app.models.common_model import Genre, Position, ProfilePositionLink, Region
from app.models.user_model import Profile, User


class ProfileService:
    async def get_profile_by_user_id(
        self, db: AsyncSession, user_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> tuple[Profile | None, bool]:
        """
        특정 사용자의 프로필을 상세 정보와 함께 조회
        현재 로그인한 사용자의 북마크 여부도 함께 반환
        """
        # 1. 프로필과 관련 정보를 즉시 로딩(eager load)
        statement = (
            select(Profile)
            .options(
                selectinload(Profile.user),
                selectinload(Profile.regions),
                selectinload(Profile.position_links).selectinload(
                    ProfilePositionLink.position
                ),
                selectinload(Profile.position_links).selectinload(
                    ProfilePositionLink.experience_level
                ),
                selectinload(Profile.genres),
            )
            .where(Profile.user_id == user_id)
        )
        result = await db.execute(statement)
        profile = result.scalar_one_or_none()

        if not profile:
            return None, False

        # 2. 현재 로그인한 사용자가 이 프로필을 북마크했는지 확인
        bookmark_statement = select(UserBookmark).where(
            UserBookmark.user_id == current_user_id,
            UserBookmark.bookmarked_user_id == user_id,
        )
        bookmark_result = await db.execute(bookmark_statement)
        is_bookmarked = bookmark_result.scalar_one_or_none() is not None

        return profile, is_bookmarked

    async def get_profile_list(
        self,
        db: AsyncSession,
        current_user_id: uuid.UUID,
        bookmarked: bool,
        limit: int,
        cursor: Optional[str],
        nickname: Optional[str],
        region_ids: Optional[List[uuid.UUID]],
        position_ids: Optional[List[uuid.UUID]],
        genre_ids: Optional[List[uuid.UUID]],
        experience_level_ids: Optional[List[uuid.UUID]],
        sort_by: str,
        order_by: str,
    ) -> Sequence[Profile]:
        """다양한 조건으로 프로필 목록을 조회"""

        # 1. 기본 쿼리 생성 (관련 테이블들을 미리 JOIN하여 N+1 문제 방지)
        statement = (
            select(Profile)
            .join(Profile.user)
            .options(
                selectinload(Profile.user),
                selectinload(Profile.regions),
                selectinload(Profile.position_links).selectinload(
                    ProfilePositionLink.position
                ),
                selectinload(Profile.position_links).selectinload(
                    ProfilePositionLink.experience_level
                ),
                selectinload(Profile.genres),
            )
        )

        if bookmarked:
            statement = statement.join(
                UserBookmark, Profile.user_id == UserBookmark.bookmarked_user_id
            ).where(UserBookmark.user_id == current_user_id)

        # 2. 필터링 조건 추가
        if nickname:
            statement = statement.where(User.nickname.ilike(f"%{nickname}%"))
        if region_ids:
            statement = statement.join(Profile.regions).where(Region.id.in_(region_ids))
        if position_ids:
            statement = statement.where(
                Profile.positions.any(Position.id.in_(position_ids))
            )
        if genre_ids:
            statement = statement.join(Profile.genres).where(Genre.id.in_(genre_ids))
        if experience_level_ids:
            statement = statement.join(Profile.position_links).where(
                ProfilePositionLink.experience_level_id.in_(experience_level_ids)
            )

        statement = statement.distinct()

        # 3. 정렬 조건 설정
        sort_column = getattr(Profile, f"{sort_by}_count", Profile.created_at)
        if order_by == "desc":
            order_expression = col(sort_column).desc()
        else:
            order_expression = col(sort_column).asc()

        statement = statement.order_by(order_expression, col(Profile.id).desc())

        # 4. 커서 기반 페이지네이션
        if cursor:
            # cursor는 '정렬값_고유ID' 형태 (예: '123_uuid' 또는 'timestamp_uuid')
            cursor_value, cursor_id = cursor.rsplit("_", 1)

            # 정렬 방향에 따라 부등호 결정
            op = (
                col(sort_column) < cursor_value
                if order_by == "desc"
                else col(sort_column) > cursor_value
            )

            statement = statement.where(
                (op)
                | ((col(sort_column) == cursor_value) & (col(Profile.id) < cursor_id))
            )

        statement = statement.limit(limit)

        result = await db.execute(statement)
        return result.scalars().all()


profile_service = ProfileService()
