import uuid
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from app.api.v1.recruiting_router import SortBy
from app.crud.comment_crud import get_comment_by_id
from app.crud.recruiting_crud import (
    create_comment,
    create_recruiting,
    delete_recruiting,
    get_recruiting_by_id,
    get_recruiting_detail,
    get_recruiting_list,
    update_recruiting_detail,
    update_recruiting_is_closed_status,
)
from app.exceptions.exceptions import (
    CommentNotFound,
    NotFirstParentComment,
    PostNotFound,
    UserNotRecruitingPostOwner,
)
from app.schemas.comment_schema import CommentContentRequest
from app.schemas.recruiting_schema import (
    GetRecruitingCursorResponse,
    GetRecruitingDetailResponse,
    RecruitingDetailRequest,
)


# FR-011: 구인글 목록 조회
async def service_get_recruiting_list(
    db: AsyncSession,
    current_user_id: uuid.UUID,
    limit: int,
    cursor: uuid.UUID | None,
    author: str | None,
    bookmarks: str | None,
    search_query: str | None,
    orientation: uuid.UUID | None,
    experienced_level: uuid.UUID | None,
    region_ids: list[uuid.UUID] | None,
    position_ids: list[uuid.UUID] | None,
    genre_ids: list[uuid.UUID] | None,
    sort_by: "SortBy",
) -> GetRecruitingCursorResponse:

    # CRUD 레이어를 호출
    return await get_recruiting_list(
        db,
        current_user_id=current_user_id,
        limit=limit,
        cursor=cursor,
        author=author,
        bookmarks=bookmarks,
        search_query=search_query,
        orientation=orientation,
        experienced_level=experienced_level,
        region_ids=region_ids,
        position_ids=position_ids,
        genre_ids=genre_ids,
        sort_by=sort_by,
    )


# FR-014: 구인글 생성
async def service_create_recruiting(
    db: AsyncSession,
    current_user_id: uuid.UUID,
    create_recruiting_request: RecruitingDetailRequest,
) -> None:
    await create_recruiting(db, current_user_id, create_recruiting_request)


# FR-012: 구인글 상세 조회
async def service_get_recruiting_detail(
    db: AsyncSession,
    post_id: uuid.UUID,
    current_user_id: uuid.UUID,
) -> GetRecruitingDetailResponse:

    # CRUD 레이어를 호출하여 id 여부 확인
    post = await get_recruiting_by_id(db, post_id=post_id)
    if not post:
        raise PostNotFound()

    get_recruiting_detail_response = await get_recruiting_detail(
        db, post, current_user_id
    )

    return get_recruiting_detail_response


# FR-015: 구인글 수정
async def service_update_recruiting_detail(
    db: AsyncSession,
    post_id: uuid.UUID,
    current_user_id: uuid.UUID,
    update_recruiting_detail_request: RecruitingDetailRequest,
) -> None:

    # CRUD 레이어를 호출하여 id 여부 확인
    post = await get_recruiting_by_id(db, post_id=post_id)
    if not post:
        raise PostNotFound()

    # 본인이 작성한 구인글인지 여부 확인
    if current_user_id != post.user_id:
        raise UserNotRecruitingPostOwner()

    # 게시글이 있다면, 정보를 수정하고 저장
    await update_recruiting_detail(db, post, update_recruiting_detail_request)


# FR-016: 구인글 마감 상태 변경
async def service_update_recruiting_is_closed_status(
    db: AsyncSession, post_id: uuid.UUID, current_user_id: uuid.UUID, is_closed: bool
) -> None:

    # CRUD 레이어 호출
    post = await get_recruiting_by_id(db, post_id=post_id)
    if not post:
        raise PostNotFound()

    # 본인이 작성한 구인글 여부 확인
    if current_user_id != post.user_id:
        raise UserNotRecruitingPostOwner()

    # 구인글이 있다면, 마감 상태를 변경
    await update_recruiting_is_closed_status(db, post, is_closed)


# FR-017: 구인글 삭제
async def service_delete_recruiting(
    db: AsyncSession, post_id: uuid.UUID, current_user_id: uuid.UUID
) -> None:

    # CRUD 레이어 호출
    post = await get_recruiting_by_id(db, post_id=post_id)
    if not post:
        raise PostNotFound()

    # 본인이 작성한 구인글 여부 확인
    if current_user_id != post.user_id:
        raise UserNotRecruitingPostOwner()

    # 구인글이 있다면, 삭제
    await delete_recruiting(db, post)


### Comment ###


# FR-018: 댓글 작성
async def service_create_comment(
    db: AsyncSession,
    current_user_id: uuid.UUID,
    post_id: uuid.UUID,
    create_comment_request: CommentContentRequest,
) -> None:
    post = await get_recruiting_by_id(db, post_id)
    if not post:
        raise PostNotFound()

    if create_comment_request.parent_comment_id:
        parent_comment = await get_comment_by_id(
            db, create_comment_request.parent_comment_id
        )
        if not parent_comment:
            raise CommentNotFound()
        if parent_comment.parent_comment_id:  # 추가!
            raise NotFirstParentComment()

    await create_comment(db, current_user_id, post, create_comment_request)
