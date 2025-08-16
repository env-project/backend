import uuid
from typing import Optional

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import (
    ExperienceLevel,
    Genre,
    Orientation,
    Position,
    Profile,
    RecruitingPost,
    RecruitingPostGenreLink,
    RecruitingPostPositionLink,
    RecruitingPostRegionLink,
    RecruitmentType,
    Region,
    User,
)
from app.schemas.recruiting_schema import (
    GetGenreResponse,
    GetOrientationResponse,
    GetPositionResponse,
    GetRecruitingDetailResponse,
    GetRecruitmentTypeResponse,
    GetRegionResponse,
    GetUserProfileResponse,
    RecruitingDetailRequest,
)


async def get_recruiting_by_id(
    db: AsyncSession, post_id: uuid.UUID
) -> RecruitingPost | None:
    """
    post_id로 구인글을 조회합니다.
    """
    stmt = select(RecruitingPost).where(RecruitingPost.id == post_id)
    result = await db.execute(stmt)

    return result.scalars().first()


# FR-014: 구인글 생성
async def create_recruiting(
    db: AsyncSession,
    create_recruiting_request: RecruitingDetailRequest,
) -> None:
    # 요청 데이터를 ORM 객체로 변환
    new_post = RecruitingPost(
        user_id=create_recruiting_request.user_id,
        title=create_recruiting_request.title,
        content=create_recruiting_request.content,
        band_name=create_recruiting_request.band_name,
        band_composition=create_recruiting_request.band_composition,
        activity_time=create_recruiting_request.activity_time,
        contact_info=create_recruiting_request.contact_info,
        application_method=create_recruiting_request.application_method,
        practice_frequency_time=create_recruiting_request.practice_frequency_time,
        other_conditions=create_recruiting_request.other_conditions,
        orientation_id=create_recruiting_request.orientation_id,
        recruitment_type_id=create_recruiting_request.recruitment_type_id,
    )

    # 데이터베이스에 추가
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    post_id = new_post.id

    # None이 아닐 때만 돌아간다.
    # Region 관계 재설정
    if create_recruiting_request.region_ids:
        for region_id in create_recruiting_request.region_ids:
            new_region_link = RecruitingPostRegionLink(
                post_id=post_id,
                region_id=region_id,
            )
            db.add(new_region_link)

    # Genre 관계 재설정
    if create_recruiting_request.genre_ids:
        for genre_id in create_recruiting_request.genre_ids:
            new_genre_link = RecruitingPostGenreLink(
                post_id=post_id,
                genre_id=genre_id,
            )
            db.add(new_genre_link)

    # Position 관계 재설정
    if create_recruiting_request.positions:
        for position in create_recruiting_request.positions:
            new_position_link = RecruitingPostPositionLink(
                post_id=post_id,
                position_id=position.position_id,
                desired_experience_level_id=position.experienced_level_id,
            )
            db.add(new_position_link)

    await db.commit()


# FR-012: 구인글 상세 조회
async def get_recruiting_detail(
    db: AsyncSession,
    post: RecruitingPost,
    current_user_id: Optional[uuid.UUID] = None,
) -> Optional[GetRecruitingDetailResponse]:
    post_id = post.id

    # 2. Fetch all counts and boolean flags
    # Get total comments count
    # comments_count_stmt = select(func.count(Comment.id)).where(
    #     Comment.post_id == post_id
    # )
    # comments_count = (await db.execute(comments_count_stmt)).scalar_one()
    #
    # # Get total bookmarks count
    # bookmarks_count_stmt = select(func.count(PostBookmark.user_id)).where(
    #     PostBookmark.post_id == post_id
    # )
    # bookmarks_count = (await db.execute(bookmarks_count_stmt)).scalar_one()
    #
    # # Get total views count
    # views_count_stmt = select(func.count(RecruitingPostView.user_id)).where(
    #     RecruitingPostView.post_id == post_id
    # )
    # views_count = (await db.execute(views_count_stmt)).scalar_one()

    # Check if the current user is the owner
    # is_owner = (current_user_id is not None) and (current_user_id == post.user_id)

    # Check if the post is bookmarked by the current user
    # is_bookmarked = False
    # if current_user_id:
    #     bookmark_stmt = select(PostBookmark).where(
    #         PostBookmark.post_id == post_id, PostBookmark.user_id == current_user_id
    #     )
    #     is_bookmarked = (
    #         await db.execute(bookmark_stmt)
    #     ).scalar_one_or_none() is not None

    # Increment views_count
    # if current_user_id and not is_owner:
    #     insert_view_stmt = (
    #         insert(RecruitingPostView)
    #         .values(post_id=post_id, user_id=current_user_id)
    #         .on_conflict_do_nothing()
    #     )
    #     await db.execute(insert_view_stmt)
    #     await db.commit()
    #     # Refresh the views count after adding a new view
    #     views_count = (await db.execute(views_count_stmt)).scalar_one()

    # Author Profile
    # 2. Fetch the author's User information (this is mandatory)
    user_stmt = select(User).where(User.id == post.user_id)
    user = (await db.execute(user_stmt)).scalar_one_or_none()

    if not user:
        # 이 경우는 데이터 무결성 문제이므로 에러를 발생시키는 것이 적절합니다.
        raise ValueError(f"Author with user_id {post.user_id} not found.")

    # 3. Fetch the author's Profile information (this is optional)
    profile_stmt = select(Profile).where(Profile.user_id == user.id)
    profile = (await db.execute(profile_stmt)).scalar_one_or_none()

    # 4. Construct the author response with a conditional check
    author_response = GetUserProfileResponse(
        user_id=user.id,
        nickname=user.nickname,
        image_url=profile.image_url if profile else None,
    )

    # Orientation
    orientation_stmt = select(Orientation).where(Orientation.id == post.orientation_id)
    orientation = (await db.execute(orientation_stmt)).scalar_one()
    orientation_response = GetOrientationResponse(
        id=orientation.id, name=orientation.name
    )

    # Recruitment Type
    recruitment_type_stmt = select(RecruitmentType).where(
        RecruitmentType.id == post.recruitment_type_id
    )
    recruitment_type = (await db.execute(recruitment_type_stmt)).scalar_one()
    recruitment_type_response = GetRecruitmentTypeResponse(
        id=recruitment_type.id, name=recruitment_type.name
    )

    # Regions
    regions_stmt = (
        select(Region)
        .join(RecruitingPostRegionLink)
        .where(RecruitingPostRegionLink.post_id == post_id)
    )
    regions_result = (await db.execute(regions_stmt)).scalars().all()
    regions_response = [GetRegionResponse(id=r.id, name=r.name) for r in regions_result]

    # Genres
    genres_stmt = (
        select(Genre)
        .join(RecruitingPostGenreLink)
        .where(RecruitingPostGenreLink.post_id == post_id)
    )
    genres_result = (await db.execute(genres_stmt)).scalars().all()
    genres_response = [GetGenreResponse(id=g.id, name=g.name) for g in genres_result]

    # Positions with experience levels
    positions_stmt = (
        select(
            RecruitingPostPositionLink.position_id,
            Position.name.label("position_name"),
            RecruitingPostPositionLink.desired_experience_level_id.label(
                "experienced_level_id"
            ),
            ExperienceLevel.name.label("experienced_level_name"),
        )
        .join(Position, RecruitingPostPositionLink.position_id == Position.id)
        .join(
            ExperienceLevel,
            RecruitingPostPositionLink.desired_experience_level_id
            == ExperienceLevel.id,
        )
        .where(RecruitingPostPositionLink.post_id == post_id)
    )
    positions_result = (await db.execute(positions_stmt)).all()
    positions_response = [
        GetPositionResponse(
            position_id=p.position_id,
            position_name=p.position_name,
            experienced_level_id=p.experienced_level_id,
            experienced_level_name=p.experienced_level_name,
        )
        for p in positions_result
    ]

    # 5. Construct the final response object
    return GetRecruitingDetailResponse(
        id=post.id,
        created_at=post.created_at,
        author=author_response,
        title=post.title,
        content=post.content,
        # image_url=post.image_url,
        band_name=post.band_name,
        band_composition=post.band_composition,
        activity_time=post.activity_time,
        contact_info=post.contact_info,
        application_method=post.application_method,
        practice_frequency_time=post.practice_frequency_time,
        other_conditions=post.other_conditions,
        is_closed=post.is_closed,
        # is_owner=is_owner,
        # is_bookmarked=is_bookmarked,
        views_count=post.views_count,
        comments_count=post.comments_count,
        bookmarks_count=post.bookmarks_count,
        orientation=orientation_response,
        recruitment_type=recruitment_type_response,
        regions=regions_response,
        genres=genres_response,
        positions=positions_response,
    )


# FR-015: 구인글 수정
async def update_recruiting_detail(
    db: AsyncSession,
    post: RecruitingPost,
    update_recruiting_detail_request: RecruitingDetailRequest,
) -> None:
    # Update fields
    post.title = update_recruiting_detail_request.title
    post.content = update_recruiting_detail_request.content

    post.band_name = update_recruiting_detail_request.band_name
    post.band_composition = update_recruiting_detail_request.band_composition
    post.activity_time = update_recruiting_detail_request.activity_time
    post.contact_info = update_recruiting_detail_request.contact_info
    post.application_method = update_recruiting_detail_request.application_method
    post.practice_frequency_time = (
        update_recruiting_detail_request.practice_frequency_time
    )
    post.other_conditions = update_recruiting_detail_request.other_conditions

    post.orientation_id = update_recruiting_detail_request.orientation_id
    post.recruitment_type_id = update_recruiting_detail_request.recruitment_type_id

    post_id = post.id

    # None이 아닐 때만 돌아간다.
    # Region 관계 재설정
    if update_recruiting_detail_request.region_ids:
        await db.execute(
            delete(RecruitingPostRegionLink).where(
                RecruitingPostRegionLink.post_id == post_id
            )
        )
        for region_id in update_recruiting_detail_request.region_ids:
            new_region_link = RecruitingPostRegionLink(
                post_id=post_id,
                region_id=region_id,
            )
            db.add(new_region_link)

    # Genre 관계 재설정
    if update_recruiting_detail_request.genre_ids:
        await db.execute(
            delete(RecruitingPostGenreLink).where(
                RecruitingPostGenreLink.post_id == post_id
            )
        )
        for genre_id in update_recruiting_detail_request.genre_ids:
            new_genre_link = RecruitingPostGenreLink(
                post_id=post_id,
                genre_id=genre_id,
            )
            db.add(new_genre_link)

    # Position 관계 재설정
    if update_recruiting_detail_request.positions:
        await db.execute(
            delete(RecruitingPostPositionLink).where(
                RecruitingPostPositionLink.post_id == post_id
            )
        )
        for position in update_recruiting_detail_request.positions:
            new_position_link = RecruitingPostPositionLink(
                post_id=post_id,
                position_id=position.position_id,
                desired_experience_level_id=position.experienced_level_id,
            )
            db.add(new_position_link)

    await db.commit()
    await db.refresh(post)


# FR-016: 구인글 마감 상태 변경
async def update_recruiting_is_closed_status(
    db: AsyncSession, post: RecruitingPost, is_closed: bool
) -> None:
    post.is_closed = is_closed
    await db.commit()
    await db.refresh(post)


# FR-017: 구인글 삭제
async def delete_recruiting(db: AsyncSession, post: RecruitingPost) -> None:
    await db.delete(post)
    await db.commit()


# def create_user(db: Session, user: UserCreate) -> User:
#     """새로운 사용자를 생성합니다."""
#     db_user = User.model_validate(user)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user
