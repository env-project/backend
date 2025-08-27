# app/api/v1/endpoints/profile.py
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.v1.dependencies import get_current_user_or_none
from app.core.database import get_async_session
from app.models.bookmark_model import UserBookmark
from app.models.user_model import User
from app.schemas.profile import (
    PositionWithExperienceRead,
    ProfileDetailRead,
    ProfileListRead,
    ProfileListResponse,
)
from app.services.profile_service import profile_service

router = APIRouter()


@router.get("", response_model=ProfileListResponse)
async def get_profiles(
    db: AsyncSession = Depends(get_async_session),
    current_user: Optional[User] = Depends(get_current_user_or_none),
    limit: int = Query(20, gt=0, le=100),
    cursor: Optional[str] = Query(None),
    nickname: Optional[str] = Query(None),
    region_ids_str: Optional[str] = Query(None, alias="region_ids"),
    position_ids_str: Optional[str] = Query(None, alias="position_ids"),
    genre_ids_str: Optional[str] = Query(None, alias="genre_ids"),
    experience_level_ids_str: Optional[str] = Query(None, alias="experience_level_ids"),
    sort_by: str = Query("latest", enum=["latest", "bookmarks", "views"]),
    bookmarked: bool = Query(False, description="내가 북마크한 프로필만 조회"),
    order_by: str = Query("desc", enum=["asc", "desc"]),
):
    """타 사용자 프로필 목록을 조회"""

    # 콤마로 구분된 문자열을 UUID 리스트로 파싱
    def parse_uuid_list(id_str: Optional[str]) -> Optional[List[uuid.UUID]]:
        if not id_str:
            return None
        try:
            return [uuid.UUID(i.strip()) for i in id_str.split(",")]
        except ValueError:
            raise HTTPException(
                status_code=422, detail="Invalid UUID format in query parameters."
            )

    region_ids = parse_uuid_list(region_ids_str)
    position_ids = parse_uuid_list(position_ids_str)
    genre_ids = parse_uuid_list(genre_ids_str)
    experience_level_ids = parse_uuid_list(experience_level_ids_str)
    profiles = await profile_service.get_profile_list(
        db=db,
        current_user_id=current_user.id if current_user else None,
        limit=limit,
        cursor=cursor,
        nickname=nickname,
        region_ids=region_ids,
        position_ids=position_ids,
        genre_ids=genre_ids,
        experience_level_ids=experience_level_ids,
        sort_by=sort_by,
        bookmarked=bookmarked,
        order_by=order_by,
    )

    # is_bookmarked 로직
    bookmarked_user_ids = set()
    if current_user and profiles:
        profile_user_ids = [p.user_id for p in profiles]
        statement = select(UserBookmark.bookmarked_user_id).where(
            UserBookmark.user_id == current_user.id,
            UserBookmark.bookmarked_user_id.in_(profile_user_ids),
        )
        result = await db.execute(statement)
        bookmarked_user_ids = set(result.scalars().all())

    # 다음 페이지를 위한 next_cursor 생성
    next_cursor = None
    if profiles and len(profiles) == limit:
        last_profile = profiles[-1]
        sort_value = getattr(last_profile, f"{sort_by}_count", last_profile.created_at)
        next_cursor = f"{sort_value}_{last_profile.id}"

    # 최종 응답 데이터 생성
    response_profiles = []
    for p in profiles:
        positions_data = [
            PositionWithExperienceRead.from_link(link)
            for link in getattr(p, "position_links", []) or []
        ]

        response_profiles.append(
            ProfileListRead(
                user_id=p.user_id,
                email=getattr(p.user, "email", None),
                nickname=getattr(p.user, "nickname", None),
                image_url=getattr(p, "image_url", None),
                is_bookmarked=p.user_id in bookmarked_user_ids,
                regions=getattr(p, "regions", []) or [],
                positions=positions_data or [],
                genres=getattr(p, "genres", []) or [],
            )
        )

    return ProfileListResponse(next_cursor=next_cursor, profiles=response_profiles)


@router.get("/{user_id}", response_model=ProfileDetailRead)
async def get_profile(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: Optional[User] = Depends(get_current_user_or_none),
):
    """타 사용자 프로필 상세 정보를 조회"""
    current_user_id = current_user.id if current_user else None
    profile, is_bookmarked = await profile_service.get_profile_by_user_id(
        db=db, user_id=user_id, current_user_id=current_user_id
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )

    # 비공개 프로필인 경우, 본인이 아니면 접근을 거부
    if not profile.is_public and (
        not current_user or profile.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="This profile is private"
        )

    # 최종 응답 데이터를 스키마에 맞게 조합
    positions_data = [
        PositionWithExperienceRead.from_link(link)
        for link in getattr(profile, "position_links", []) or []
    ]

    return ProfileDetailRead(
        email=getattr(profile.user, "email", None),
        nickname=getattr(profile.user, "nickname", None),
        image_url=getattr(profile, "image_url", None),
        is_public=bool(getattr(profile, "is_public", True)),
        is_bookmarked=bool(is_bookmarked),
        regions=getattr(profile, "regions", []) or [],
        positions=positions_data or [],
        genres=getattr(profile, "genres", []) or [],
    )
