import logging
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.database import get_async_session
from app.exceptions.exceptions import CommentNotFound, UserNotCommentOwner
from app.schemas.comment_schema import CommentContentRequest
from app.services.comment_service import (
    service_delete_comment,
    service_get_comment_list,
    service_update_comment_content,
)

comment_router = APIRouter()

logger = logging.getLogger(__name__)


# FR-019: 댓글 목록 조회
@comment_router.get(
    "",
    description="""
    - 다양한 조건으로 특정 구인글의 댓글 목록을 조회합니다.
    - 다양한 조건으로 내 프로필에서 내가 작성한 댓글을 조회합니다.

    Args:

    Returns:
        GetCursorCommentResponse: next_cursor와 댓글의 상세 내용을 담는 객체

        성공
        - HTTP_200_OK: 
            처리 성공

        실패 (with specific error msg)
        - HTTP_401_UNAUTHORIZED: 
            사용자가 존재하지 않을 때 
                (아마도...? Error Code는 다를수도 있습니다.)
                (아직 Auth쪽 구현이 안되었습니다. 구현 후 가능)
            본인 댓글이 아닐 때

        - HTTP_404_NOT_FOUND: 
            댓글이 존재하지 않을 때

        - HTTP_422_UNPROCESSABLE_ENTITY: 
            wrong json type
            FastAPI server에서 자동 에러 응답

        - HTTP_500_INTERNAL_SERVER_ERROR: 
            예상치 못한 서버 오류(DB 연결 오류, 타입 에러 등 버그)
    """,
    status_code=status.HTTP_200_OK,
)
async def api_get_comment_list(
    post_id: uuid.UUID = Query(...),  # required
    author: Optional[str] = Query(default=None),  # me
    limit: int = Query(default=10, le=10),
    cursor: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_async_session),
    # current_user_id: uuid.UUID = Depends(get_current_user),
) -> None:
    # OAuth2
    current_user_id = None
    if author:
        current_user_id = uuid.UUID("01989fa6-6cc6-7156-a3e1-d038015598db")  # admin
        # current_user_id = uuid.UUID("01989c33-5fa0-7925-9a6e-8bc913bbc5e3")  # test_user

    try:
        await service_get_comment_list(
            db, current_user_id, post_id, author, limit, cursor
        )
    except CommentNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UserNotCommentOwner:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="본인이 작성한 글만 수정할 수 있습니다.",
        )
    except Exception as e:
        logger.error(
            f"Unexpected error in api_change_is_closed_status: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버에 예상치 못한 오류가 발생했습니다.",
        )

    await db.close()


# FR-020: 댓글 수정
@comment_router.patch(
    "/{comment_id}",
    description="""
    본인이 작성한 댓글의 내용을 수정합니다.

    Args:
        CommentContentRequest: 수정할 댓글의 필드 내용을 담는 객체

    Returns:
        성공
        - HTTP_200_OK: 
            처리 성공

        실패 (with specific error msg)
        - HTTP_401_UNAUTHORIZED: 
            사용자가 존재하지 않을 때 
                (아마도...? Error Code는 다를수도 있습니다.)
                (아직 Auth쪽 구현이 안되었습니다. 구현 후 가능)
            본인 댓글이 아닐 때

        - HTTP_404_NOT_FOUND: 
            댓글이 존재하지 않을 때

        - HTTP_422_UNPROCESSABLE_ENTITY: 
            wrong json type
            FastAPI server에서 자동 에러 응답

        - HTTP_500_INTERNAL_SERVER_ERROR: 
            예상치 못한 서버 오류(DB 연결 오류, 타입 에러 등 버그)
    """,
    status_code=status.HTTP_200_OK,
)
async def api_update_comment_content(
    comment_id: uuid.UUID,
    create_comment_request: CommentContentRequest,
    db: AsyncSession = Depends(get_async_session),
    # current_user_id: uuid.UUID = Depends(get_current_user_id),
) -> None:
    # OAuth2
    current_user_id = uuid.UUID("01989fa6-6cc6-7156-a3e1-d038015598db")  # admin
    # current_user_id = uuid.UUID("01989c33-5fa0-7925-9a6e-8bc913bbc5e3")  # test_user

    try:
        await service_update_comment_content(
            db,
            current_user_id,
            comment_id,
            create_comment_request,
        )
    except CommentNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UserNotCommentOwner:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="본인이 작성한 글만 수정할 수 있습니다.",
        )
    except Exception as e:
        logger.error(
            f"Unexpected error in api_change_is_closed_status: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버에 예상치 못한 오류가 발생했습니다.",
        )

    await db.close()


# FR-021: 댓글 삭제
@comment_router.delete(
    "/{comment_id}",
    description="""
    본인이 작성한 댓글을 삭제합니다.

    Args:

    Returns:
        성공
        - HTTP_204_NO_CONTENT: 
            처리 성공

        실패 (with specific error msg)
        - HTTP_401_UNAUTHORIZED: 
            사용자가 존재하지 않을 때 
                (아마도...? Error Code는 다를수도 있습니다.)
                (아직 Auth쪽 구현이 안되었습니다. 구현 후 가능)
            본인 댓글이 아닐 때

        - HTTP_404_NOT_FOUND: 
            댓글이 존재하지 않을 때

        - HTTP_422_UNPROCESSABLE_ENTITY: 
            wrong json type
            FastAPI server에서 자동 에러 응답

        - HTTP_500_INTERNAL_SERVER_ERROR: 
            예상치 못한 서버 오류(DB 연결 오류, 타입 에러 등 버그)
    """,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def api_delete_comment(
    comment_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    # current_user_id: uuid.UUID = Depends(get_current_user_id),
) -> None:
    # OAuth2
    current_user_id = uuid.UUID("01989fa6-6cc6-7156-a3e1-d038015598db")  # admin
    # current_user_id = uuid.UUID("01989c33-5fa0-7925-9a6e-8bc913bbc5e3")  # test_user

    try:
        await service_delete_comment(
            db,
            current_user_id,
            comment_id,
        )
    except CommentNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UserNotCommentOwner:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="본인이 작성한 글만 삭제할 수 있습니다.",
        )
    except Exception as e:
        logger.error(
            f"Unexpected error in api_change_is_closed_status: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버에 예상치 못한 오류가 발생했습니다.",
        )

    await db.close()
