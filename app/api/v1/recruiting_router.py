import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.database import get_async_session
from app.exceptions.exceptions import (
    CommentNotFound,
    PostNotFound,
    UserNotRecruitingPostOwner,
)
from app.schemas.comment_schema import CommentContentRequest
from app.schemas.enums import IsAuthor, IsBookmarked, SortBy
from app.schemas.recruiting_schema import (
    GetRecruitingCursorResponse,
    GetRecruitingDetailResponse,
    RecruitingDetailRequest,
)
from app.services.recruiting_service import (
    service_create_recruiting,
    service_delete_recruiting,
    service_get_recruiting_detail,
    service_update_recruiting_detail,
    service_update_recruiting_is_closed_status,
)

# 로거 설정 (별도의 설정 파일 필요)
logger = logging.getLogger(__name__)

recruiting_router = APIRouter(
    prefix="/api/v1/recruiting-posts", tags=["recruiting"], redirect_slashes=False
)


# test 용 user_id
current_user_id = uuid.UUID("0198a853-9870-7b73-8a54-cfc1e8a7dadf")  # admin
# current_user_id = uuid.UUID("0198a853-a345-7be0-9da7-a960023adcab")  # test_user
# current_user_id = uuid.UUID("0198b8b3-56e6-71d7-b766-c25fa414db94")


# FR-011: 구인글 목록 조회
@recruiting_router.get(
    "",
    description="""
    구인글 목록 조회(FR-011)
    """,
    response_model=GetRecruitingCursorResponse,
    status_code=status.HTTP_200_OK,
)
async def api_get_recruiting(
    limit: Optional[int] = Query(20, le=20),
    cursor: Optional[uuid.UUID] = Query(None),
    author: Optional[IsAuthor] = Query(None),
    bookmarks: Optional[IsBookmarked] = Query(None),
    search_query: Optional[str] = Query(None),
    orientation: Optional[uuid.UUID] = Query(None),
    experienced_level: Optional[uuid.UUID] = Query(None),
    region_ids: Optional[List[uuid.UUID]] = Query(None),
    position_ids: Optional[List[uuid.UUID]] = Query(None),
    genre_ids: Optional[List[uuid.UUID]] = Query(None),
    sort_by: SortBy = Query(SortBy.LATEST),
    db: AsyncSession = Depends(get_async_session),
) -> GetRecruitingCursorResponse:

    # current_user_id = None  # 로그인 안 한 사용자

    # OAuth2
    # if author == "me" or bookmarks == "me":  # 1차적으로 인증
    #     current_user_id = get_current_user()
    # elif has_bearer_auto_error_false():  # 그냥 로그인한 사용자 인증
    #     current_user_id = get_current_user()

    # Bearer 빼는 로직
    # from fastapi.security import OAuth2PasswordBearer

    get_recruiting_cursor_response = await service_get_recruiting_list(
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
    return get_recruiting_cursor_response


# FR-014: 구인글 작성
@recruiting_router.post(
    "",
    description="""
    구인글 작성(FR-014)
    """,
    status_code=status.HTTP_201_CREATED,
)
async def api_create_recruiting(
    create_recruiting_request: RecruitingDetailRequest,
    db: AsyncSession = Depends(get_async_session),
    # current_user_id: uuid.UUID = Depends(get_current_user_id),# E422
) -> None:

    # OAuth2
    # current_user_id = get_current_user()

    try:
        await service_create_recruiting(db, current_user_id, create_recruiting_request)
    except Exception as e:
        logger.error(
            f"Unexpected error in api_change_is_closed_status: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버에 예상치 못한 오류가 발생했습니다.",
        )


# FR-012: 구인글 상세 조회
@recruiting_router.get(
    "/{post_id}",
    description="""
    구인글 상세 조회(FR-012)
    """,
    response_model=GetRecruitingDetailResponse,
    status_code=status.HTTP_200_OK,
)
async def api_get_recruiting_detail(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
) -> GetRecruitingDetailResponse:

    # current_user_id = None  # 로그인 안 한 사용자

    # OAuth2
    # if has_bearer_auto_error_false():  # 그냥 로그인한 사용자 인증
    #     current_user_id = get_current_user()

    try:
        get_recruiting_detail_response = await service_get_recruiting_detail(
            db, post_id=post_id, current_user_id=current_user_id
        )
    except PostNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error in api_change_is_closed_status: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버에 예상치 못한 오류가 발생했습니다.",
        )

    return get_recruiting_detail_response


# FR-015: 구인글 수정
@recruiting_router.patch(
    "/{post_id}",
    description="""
    구인글 수정(FR-015)
    """,
    status_code=status.HTTP_200_OK,
)
async def api_update_recruiting_detail(
    post_id: uuid.UUID,
    update_recruiting_detail_request: RecruitingDetailRequest,
    db: AsyncSession = Depends(get_async_session),
) -> None:

    # OAuth2
    # current_user_id = get_current_user()

    try:
        await service_update_recruiting_detail(
            db,
            post_id=post_id,
            current_user_id=current_user_id,
            update_recruiting_detail_request=update_recruiting_detail_request,
        )
    except PostNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UserNotRecruitingPostOwner as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    except Exception as e:
        logger.error(
            f"Unexpected error in api_change_is_closed_status: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버에 예상치 못한 오류가 발생했습니다.",
        )

    await db.close()


# FR-016: 구인글 마감 상태 변경
@recruiting_router.patch(
    "/{post_id}/status",
    description="""
    구인글 마감 상태 변경(FR-016)
    """,
    status_code=status.HTTP_200_OK,
)
async def api_update_recruiting_is_closed_status(
    post_id: uuid.UUID,
    is_closed: bool,
    db: AsyncSession = Depends(get_async_session),
) -> None:

    # OAuth2
    # current_user_id = get_current_user()

    try:
        await service_update_recruiting_is_closed_status(
            db, post_id=post_id, current_user_id=current_user_id, is_closed=is_closed
        )
    except PostNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UserNotRecruitingPostOwner as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error in api_change_is_closed_status: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버에 예상치 못한 오류가 발생했습니다.",
        )


# FR-017: 구인글 삭제
@recruiting_router.delete(
    "/{post_id}",
    description="""
    구인글 삭제(FR-017)
    """,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def api_delete_recruiting(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
) -> None:

    # OAuth2
    # current_user_id = get_current_user()

    try:
        await service_delete_recruiting(
            db, post_id=post_id, current_user_id=current_user_id
        )
    except PostNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UserNotRecruitingPostOwner as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error in api_change_is_closed_status: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버에 예상치 못한 오류가 발생했습니다.",
        )


"""
Comments
"""


# FR-018: 댓글 작성
@recruiting_router.post(
    "/{post_id}/comments",
    description="""
    댓글 작성(FR-018)
    """,
    status_code=status.HTTP_201_CREATED,
)
async def api_create_comment(
    post_id: uuid.UUID,
    create_comment_request: CommentContentRequest,
    db: AsyncSession = Depends(get_async_session),
    # current_user_id: uuid.UUID = Depends(get_current_user_id),
) -> None:

    try:
        await service_create_comment(
            db=db,
            post_id=post_id,
            current_user_id=current_user_id,
            create_comment_request=create_comment_request,
        )
    except PostNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CommentNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 부모 댓글입니다.",
        )
    except Exception as e:
        logger.error(
            f"Unexpected error in api_change_is_closed_status: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버에 예상치 못한 오류가 발생했습니다.",
        )
