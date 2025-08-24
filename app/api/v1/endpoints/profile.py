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


@router.get("/", response_model=ProfileListResponse)
async def get_profiles(
    db: AsyncSession = Depends(get_async_session),
    current_user: Optional[User] = Depends(
        get_current_user_or_none
    ),  # 아 swagger에 test기가 있네요. 주석취소했습니다.
    limit: int = Query(20, gt=0, le=100),
    cursor: Optional[str] = Query(None),
    nickname: Optional[str] = Query(None),
    region_ids: Optional[List[uuid.UUID]] = Query(None),
    position_ids: Optional[List[uuid.UUID]] = Query(None),
    genre_ids: Optional[List[uuid.UUID]] = Query(None),
    experience_level_ids: Optional[List[uuid.UUID]] = Query(None),
    sort_by: str = Query("latest", enum=["latest", "bookmarks", "views"]),
    order_by: str = Query("desc", enum=["asc", "desc"]),
):
    """타 사용자 프로필 목록을 조회"""
    current_user_id = current_user.id if current_user else None
    profiles = await profile_service.get_profile_list(
        db=db,
        current_user_id=current_user_id,
        limit=limit,
        cursor=cursor,
        nickname=nickname,
        region_ids=region_ids,
        position_ids=position_ids,
        genre_ids=genre_ids,
        experience_level_ids=experience_level_ids,
        sort_by=sort_by,
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
            PositionWithExperienceRead.from_link(link) for link in p.position_links
        ]

        response_profiles.append(
            ProfileListRead(
                user_id=p.user_id,
                email=p.user.email,
                nickname=p.user.nickname,
                image_url=p.image_url,
                is_bookmarked=p.user_id in bookmarked_user_ids,
                regions=p.regions,
                positions=positions_data,
                genres=p.genres,
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

    # 최근 활동 내역을 조회
    recent_posts = await profile_service.get_recent_posts(db=db, user_id=user_id)
    recent_comments = await profile_service.get_recent_comments(db=db, user_id=user_id)

    # 최종 응답 데이터를 스키마에 맞게 조합
    return ProfileDetailRead(
        email=profile.user.email,
        nickname=profile.user.nickname,
        image_url=profile.image_url,
        is_public=profile.is_public,
        is_bookmarked=is_bookmarked,
        regions=profile.regions,
        positions=[
            PositionWithExperienceRead.from_link(link)
            for link in profile.position_links
        ],
        genres=profile.genres,
        recent_posts=recent_posts,
        recent_comments=recent_comments,
    )
