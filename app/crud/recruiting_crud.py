import logging
import uuid

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import and_, desc, or_, select, tuple_

from app.models import (
    Comment,
    ExperienceLevel,
    Genre,
    Orientation,
    Position,
    PostBookmark,
    RecruitingPost,
    RecruitingPostGenreLink,
    RecruitingPostPositionLink,
    RecruitingPostRegionLink,
    RecruitmentType,
    Region,
    User,
)
from app.schemas.comment_schema import CreateCommentRequest
from app.schemas.enums import SortBy
from app.schemas.recruiting_schema import (
    GetGenreResponse,
    GetOrientationResponse,
    GetPositionResponse,
    GetRecruitingCursorResponse,
    GetRecruitingDetailResponse,
    GetRecruitingListResponse,
    RecruitingDetailRequest,
)

logger = logging.getLogger(__name__)


async def get_user_by_id(db: AsyncSession, author: uuid.UUID) -> RecruitingPost | None:
    """
    id로 사용자를 조회합니다.
    """
    stmt = select(User).where(User.id == author)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_recruiting_by_id(
    db: AsyncSession, post_id: uuid.UUID
) -> RecruitingPost | None:
    """
    id로 구인글을 조회합니다.
    """
    stmt = (
        select(RecruitingPost)
        .options(
            selectinload(RecruitingPost.author),
            selectinload(RecruitingPost.author).selectinload(User.profile),
            selectinload(RecruitingPost.comments),
            selectinload(RecruitingPost.regions),
            selectinload(RecruitingPost.genres),
            selectinload(RecruitingPost.positions),
            selectinload(RecruitingPost.bookmarks),
        )
        .where(RecruitingPost.id == post_id)
    )
    result = await db.execute(stmt)
    return result.scalars().first()


# FR-011: 구인글 목록 조회
async def get_recruiting_list(
    db: AsyncSession,
    current_user_id: uuid.UUID,
    limit: int,
    cursor: uuid.UUID | None,
    author: uuid.UUID | None,
    bookmarks: str | None,
    search_query: str | None,
    orientation: uuid.UUID | None,
    experienced_level: uuid.UUID | None,
    region_ids: list[uuid.UUID] | None,
    position_ids: list[uuid.UUID] | None,
    genre_ids: list[uuid.UUID] | None,
    sort_by: "SortBy",
) -> GetRecruitingCursorResponse:

    stmt = select(RecruitingPost)

    # author
    if author:
        stmt = stmt.where(RecruitingPost.user_id == author)

    # bookmarks: query+=1
    bookmarked_post_ids = []
    if current_user_id:  # 로그인한 사용자에 대해서
        bookmarked_post_id_subquery = select(PostBookmark.bookmarked_post_id).where(
            PostBookmark.user_id == current_user_id
        )
        bookmarked_posts_result = await db.execute(bookmarked_post_id_subquery)
        bookmarked_post_ids = bookmarked_posts_result.scalars().all()  # list or []
    if bookmarks == "me":
        stmt = stmt.where(RecruitingPost.id.in_(bookmarked_post_ids))

    # search_query
    if search_query:
        stmt = stmt.where(
            or_(
                RecruitingPost.title.ilike(f"%{search_query}%"),
                RecruitingPost.content.ilike(f"%{search_query}%"),
            )
        )

    if orientation:
        stmt = stmt.where(RecruitingPost.orientation_id == orientation)

    # many-to-many relationships
    if region_ids:
        stmt = stmt.where(RecruitingPost.regions.any(Region.id.in_(region_ids)))
    if genre_ids:
        stmt = stmt.where(RecruitingPost.genres.any(Genre.id.in_(genre_ids)))
    if position_ids:
        stmt = stmt.where(RecruitingPost.positions.any(Position.id.in_(position_ids)))

    """
    Should be refactored
    after re-modeling
    """
    if experienced_level:
        desired_experience_level_subquery = select(
            RecruitingPostPositionLink.post_id
        ).where(
            RecruitingPostPositionLink.desired_experience_level_id == experienced_level
        )
        stmt = stmt.where(RecruitingPost.id.in_(desired_experience_level_subquery))

    # sort_by
    sort_column_map = {
        SortBy.LATEST: RecruitingPost.created_at,
        SortBy.VIEWS: RecruitingPost.views_count,
        SortBy.COMMENTS: RecruitingPost.comments_count,
        SortBy.BOOKMARK: RecruitingPost.bookmarks_count,
    }
    sort_column = sort_column_map[sort_by]

    # cursor 부터 시작: query+=1
    if cursor:
        cursor_item_stmt = select(sort_column, RecruitingPost.created_at).where(
            RecruitingPost.id == cursor
        )
        cursor_result = await db.execute(cursor_item_stmt)
        cursor_values = cursor_result.first()

        """
        부르기 전에 구인글 삭제한 경우 처리 로직 필요
        """
        if cursor_values:
            cursor_sort_value, cursor_created_at = cursor_values
            stmt = stmt.where(  # DESC
                tuple_(sort_column, RecruitingPost.created_at)
                <= (cursor_sort_value, cursor_created_at)
            )
        # next_cursor={} where
        # offset: 많을 때

    # sort_by로 정렬, 같은 값이면 시간순
    stmt = stmt.order_by(desc(sort_column), desc(RecruitingPost.created_at))

    # Eager load related data (N+1 query issue)
    stmt = stmt.options(
        selectinload(RecruitingPost.author),
        selectinload(RecruitingPost.author).selectinload(User.profile),
        selectinload(RecruitingPost.regions),
        selectinload(RecruitingPost.genres),
        selectinload(RecruitingPost.positions),
        # recruitmenttype
        # subquery vs join
        #
    )

    # stmt query 실행: query+=1
    stmt = stmt.limit(limit + 1)  # next_cursor 넣으려고 1개 더
    result = await db.execute(stmt)
    result_rows = (
        result.all()
    )  # .all() returns a list of <class 'sqlalchemy.engine.row.Row'> objects
    print("@@@db에서 조회된 개수@@@: ", len(result_rows))

    next_cursor = None
    if len(result_rows) == limit + 1:
        next_cursor = result_rows[-1][0].__dict__["id"]
        result_rows = result_rows[:-1]

    # 직렬화
    posts_response = []

    """
    grouping
    id_list = [post_data["id"] for post_data in result_rows]
    """
    # post_obj: (RecruitingPost(),) <class 'sqlalchemy.engine.row.Row'>
    for post_obj in result_rows:
        # Row 객체를 딕셔너리로 변환
        # {'_sa_instance_state': <sqlalchemy.orm.state.InstanceState object at 0x107f23590>
        post_data = post_obj[0].__dict__

        post_id = post_data["id"]

        author_obj = post_data["author"]  # <class 'app.models.user.User'>
        post_data["author"] = {
            "id": author_obj.id,
            "nickname": author_obj.nickname,
            "image_url": (author_obj.profile.image_url if author_obj.profile else None),
        }

        # 딕셔너리에 추가 데이터 삽입
        post_data["is_owner"] = post_data["user_id"] == current_user_id

        # <class 'sqlmodel.sql._expression_select_cls.SelectOfScalar'>
        # TypeError: argument of type 'SelectOfScalar' is not iterable
        post_data["is_bookmarked"] = True if post_id in bookmarked_post_ids else False

        if post_data["orientation_id"]:
            stmt = select(Orientation).where(
                Orientation.id == post_data["orientation_id"]
            )
            result = await db.execute(stmt)
            orientation = result.scalars().first()
            post_data["orientation"] = GetOrientationResponse(
                id=orientation.id,
                name=orientation.name,
            )
        if post_data["recruitment_type_id"]:
            stmt = select(RecruitmentType).where(
                RecruitmentType.id == post_data["recruitment_type_id"]
            )
            result = await db.execute(stmt)
            recruitment_type = result.scalars().first()
            post_data["recruitment_type"] = GetOrientationResponse(
                id=recruitment_type.id,
                name=recruitment_type.name,
            )

        """
        Should be re-factored
        : RecruitingPost, Position, RecruitingPostPositionLink needs to be overhauled
        """
        # for position_obj in post_data["positions"]:  # <class 'sqlalchemy.orm.collections.InstrumentedList'>
        # query+=N
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

        # [(UUID('0198a844-cf04-711a-9087-26917d6c6fec'), '키보드', UUID('0198a844-cf07-70e8-960f-35244cea8da4'), '프로'),
        positions_result = (await db.execute(positions_stmt)).all()
        positions_response = [
            GetPositionResponse.model_validate(p) for p in positions_result
        ]
        post_data["positions"] = positions_response

        # Pydantic handles nested relationships (author, regions, etc.)
        # `from_attributes=True` in FROZEN_CONFIG
        post_dto = GetRecruitingListResponse.model_validate(post_data)
        posts_response.append(post_dto)

    return GetRecruitingCursorResponse(next_cursor=next_cursor, posts=posts_response)


# FR-014: 구인글 생성
async def create_recruiting(
    db: AsyncSession,
    current_user_id: uuid.UUID,
    create_recruiting_request: RecruitingDetailRequest,
) -> None:

    # async with db.begin():
    # 데이터를 to dict
    post_dict = create_recruiting_request.model_dump()
    post_dict["user_id"] = current_user_id

    # dict to ORM 객체
    # new_post = RecruitingPost(**post_dict)
    new_post = RecruitingPost.model_validate(post_dict)

    db.add(new_post)
    await db.flush()
    post_id = new_post.id

    # None이 아닐 때만
    # Region 관계 재설정
    if create_recruiting_request.region_ids:
        """Should be re-factored
        new_post.field eager load issue

        stmt = select(Region).where(Region.id.in_(create_recruiting_request.region_ids))
        result = await db.execute(stmt)
        post_region_link = result.scalars().all()

        # SQLAlchemy가 중간 연결 테이블을 알아서 처리
        new_post.regions = post_region_link
        """

        for region_id in create_recruiting_request.region_ids:
            new_region_link_list = []
            new_region_link = RecruitingPostRegionLink(
                post_id=post_id,
                region_id=region_id,
            )
            new_region_link_list.append(new_region_link)
        db.add_all(new_region_link_list)

    # Genre 관계 재설정
    if create_recruiting_request.genre_ids:
        new_genre_link_list = []
        for genre_id in create_recruiting_request.genre_ids:
            new_genre_link = RecruitingPostGenreLink(
                post_id=post_id,
                genre_id=genre_id,
            )
            new_genre_link_list.append(new_genre_link)
        db.add_all(new_genre_link_list)

        """ Should be re-factored
        stmt = select(Genre).where(Genre.id.in_(create_recruiting_request.genre_ids))
        result = await db.execute(stmt)
        new_post.genres = result.scalars().all()
        """

    # Position 관계 재설정
    if create_recruiting_request.positions:
        new_position_link_list = []
        for position in create_recruiting_request.positions:
            new_position_link = RecruitingPostPositionLink(
                post_id=post_id,
                position_id=position.position_id,
                desired_experience_level_id=position.experienced_level_id,
            )
            new_position_link_list.append(new_position_link)
        db.add_all(new_position_link_list)

    await db.commit()


# FR-012: 구인글 상세 조회
async def get_recruiting_detail(
    db: AsyncSession,
    post: RecruitingPost,
    current_user_id: uuid.UUID,
) -> GetRecruitingDetailResponse:

    post.views_count += 1

    post_dict = post.model_dump()

    post_dict["is_owner"] = False
    post_dict["is_bookmarked"] = False
    if current_user_id:
        post_dict["is_owner"] = True if post.user_id == current_user_id else False

        bookmarked_post_id_subquery = select(PostBookmark.bookmarked_post_id).where(
            and_(
                PostBookmark.user_id == current_user_id,
                PostBookmark.bookmarked_post_id == post.id,
            )
        )
        bookmarked_posts_result = await db.execute(bookmarked_post_id_subquery)
        bookmarked_post_id = bookmarked_posts_result.scalars().one_or_none()
        post_dict["is_bookmarked"] = True if bookmarked_post_id else False

    post_dict["author"] = {
        "id": post.author.id,
        "nickname": post.author.nickname,
        "image_url": (post.author.profile.image_url if post.author.profile else None),
    }

    if post.orientation_id:
        stmt = select(Orientation).where(Orientation.id == post.orientation_id)
        result = await db.execute(stmt)
        orientation = result.scalars().first()
        post_dict["orientation"] = GetOrientationResponse(
            id=orientation.id,
            name=orientation.name,
        )
    if post.recruitment_type_id:
        stmt = select(RecruitmentType).where(
            RecruitmentType.id == post.recruitment_type_id
        )
        result = await db.execute(stmt)
        recruitment_type = result.scalars().first()
        post_dict["recruitment_type"] = GetOrientationResponse(
            id=recruitment_type.id,
            name=recruitment_type.name,
        )
    if post.regions:
        post_dict["regions"] = [
            GetGenreResponse.model_validate(region) for region in post.regions
        ]
    if post.genres:
        post_dict["genres"] = [
            GetGenreResponse.model_validate(genre) for genre in post.genres
        ]

    if post.positions:
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
            .where(RecruitingPostPositionLink.post_id == post.id)
        )

        # [(UUID('0198a844-cf04-711a-9087-26917d6c6fec'), '키보드', UUID('0198a844-cf07-70e8-960f-35244cea8da4'), '프로'),
        positions_result = (await db.execute(positions_stmt)).all()
        positions_response = [
            GetPositionResponse.model_validate(p) for p in positions_result
        ]
        post_dict["positions"] = positions_response

    await db.commit()
    return GetRecruitingDetailResponse.model_validate(post_dict)


# FR-015: 구인글 수정
async def update_recruiting_detail(
    db: AsyncSession,
    post: RecruitingPost,
    update_recruiting_detail_request: RecruitingDetailRequest,
) -> None:
    post_id = post.id

    # to_Dict
    update_data = update_recruiting_detail_request.model_dump(
        exclude_unset=True
    )  # PATCH
    keys = update_data.keys()
    if "region_ids" in keys:
        update_data.pop("region_ids")
        # post.regions = []
    if "genre_ids" in keys:
        update_data.pop("genre_ids")
        # post.genres = []
    if "positions" in keys:
        update_data.pop("positions")
        # post.positions = []

    await db.execute(
        delete(RecruitingPostRegionLink).where(
            RecruitingPostRegionLink.post_id == post_id
        )
    )
    await db.execute(
        delete(RecruitingPostGenreLink).where(
            RecruitingPostGenreLink.post_id == post_id
        )
    )
    await db.execute(
        delete(RecruitingPostPositionLink).where(
            RecruitingPostPositionLink.post_id == post_id
        )
    )

    # new_regions, new_genres: DB에서 조회한 Region, Genre 객체 리스트
    # post.regions.extend(new_regions)
    # post.genres.extend(new_genres)
    # post.positions.extend(new_positions)

    # 관계 재설정
    """
    id 이상한 거 보냈을 때 error handling 추가해야함
    """
    if update_recruiting_detail_request.region_ids is not None:
        new_region_link_list = []
        for region_id in update_recruiting_detail_request.region_ids:
            new_region_link = RecruitingPostRegionLink(
                post_id=post_id,
                region_id=region_id,
            )
            new_region_link_list.append(new_region_link)
        # post.regions = new_region_link_list
        db.add_all(new_region_link_list)

    if update_recruiting_detail_request.genre_ids is not None:
        new_genre_link_list = []
        for genre_id in update_recruiting_detail_request.genre_ids:
            new_genre_link = RecruitingPostGenreLink(
                post_id=post_id,
                genre_id=genre_id,
            )
            new_genre_link_list.append(new_genre_link)
        db.add_all(new_genre_link_list)

    if update_recruiting_detail_request.positions is not None:
        new_position_link_list = []
        for position in update_recruiting_detail_request.positions:
            new_position_link = RecruitingPostPositionLink(
                post_id=post_id,
                position_id=position.position_id,
                desired_experience_level_id=position.experienced_level_id,
            )
            new_position_link_list.append(new_position_link)
        db.add_all(new_position_link_list)

    # setattr(object, name, value): object.name = value
    for key, value in update_data.items():
        setattr(post, key, value)

    # SQLAlchemy가 변경사항을 감지
    # 이전 관계에 대한 DELETE 쿼리와 새 관계에 대한 INSERT 쿼리 execute
    await db.commit()
    # await db.refresh(post)  # 데이터베이스 트리거


# FR-016: 구인글 마감 상태 변경
async def update_recruiting_is_closed_status(
    db: AsyncSession, post: RecruitingPost, is_closed: bool
) -> None:
    post.is_closed = is_closed
    await db.commit()


# FR-017: 구인글 삭제
async def delete_recruiting(db: AsyncSession, post: RecruitingPost) -> None:
    # async with db.begin():  # sqlalchemy.exc.InvalidRequestError: A transaction is already begun on this Session.

    # SQLModel/SQLAlchemy: 관련 Link 자동 로드 및 삭제도 해주네
    # for region in post.regions:
    #     await db.delete(region)

    await db.delete(post)
    await db.commit()


## Comment
# FR-018: 댓글 작성
async def create_comment(
    db: AsyncSession,
    current_user_id: uuid.UUID,
    post: RecruitingPost,
    create_comment_request: CreateCommentRequest,
) -> None:
    new_comment = Comment(
        post_id=post.id,
        user_id=current_user_id,
        content=create_comment_request.content,
        parent_comment_id=(
            create_comment_request.parent_comment_id
            if create_comment_request.parent_comment_id
            else None
        ),
    )

    # 해당 구인글의 comments_count 집계
    post.comments_count += 1
    db.add(new_comment)

    await db.commit()
