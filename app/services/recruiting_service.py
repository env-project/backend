import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.recruiting_crud import (
    create_recruiting,
    delete_recruiting,
    get_recruiting_by_id,
    get_recruiting_detail,
    update_recruiting_detail,
    update_recruiting_is_closed_status,
)
from app.exceptions.exceptions import PostNotFound
from app.schemas.recruiting_schema import (
    GetRecruitingDetailResponse,
    RecruitingDetailRequest,
)


# FR-014: 구인글 생성
async def service_create_recruiting(
    db: AsyncSession,
    create_recruiting_request: RecruitingDetailRequest,
) -> None:
    await create_recruiting(db, create_recruiting_request)


# FR-012: 구인글 상세 조회
async def service_get_recruiting_detail(
    db: AsyncSession,
    post_id: uuid.UUID,
) -> GetRecruitingDetailResponse:
    # CRUD 레이어를 호출하여 id 여부 확인
    post = await get_recruiting_by_id(db, post_id=post_id)
    if not post:
        raise PostNotFound()

    current_user_id = "019895ec-715b-71b7-a9f4-4494734e8171"
    get_recruiting_detail_response = await get_recruiting_detail(
        db, post, current_user_id
    )

    return get_recruiting_detail_response


# FR-015: 구인글 수정
async def service_update_recruiting_detail(
    db: AsyncSession,
    post_id: uuid.UUID,
    update_recruiting_detail_request: RecruitingDetailRequest,
) -> None:
    # CRUD 레이어를 호출하여 id 여부 확인
    post = await get_recruiting_by_id(db, post_id=post_id)
    if not post:
        raise PostNotFound()

    # 게시글이 있다면, 상태를 변경하고 저장
    await update_recruiting_detail(db, post, update_recruiting_detail_request)


# FR-016: 구인글 마감 상태 변경
async def service_update_recruiting_is_closed_status(
    db: AsyncSession, post_id: uuid.UUID, is_closed: bool
) -> None:
    # CRUD 레이어를 호출하여 id 여부 확인
    post = await get_recruiting_by_id(db, post_id=post_id)
    if not post:
        raise PostNotFound()

    # 게시글이 있다면, 상태를 변경하고 저장
    await update_recruiting_is_closed_status(db, post, is_closed)


# FR-017: 구인글 삭제
async def service_delete_recruiting(db: AsyncSession, post_id: uuid.UUID) -> None:
    # CRUD 레이어를 호출하여 id 여부 확인
    post = await get_recruiting_by_id(db, post_id=post_id)
    if not post:
        raise PostNotFound()

    # 게시글이 있다면, 게시글 삭제
    await delete_recruiting(db, post)
