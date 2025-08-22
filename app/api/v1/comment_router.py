import logging
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.v1.dependencies import get_current_user_or_none, get_current_user_required
from app.core.database import get_async_session
from app.exceptions.exceptions import (
    CommentNotFound,
    NotFirstParentComment,
    PostNotFound,
    UserNotCommentOwner,
    UserNotFound,
)
from app.schemas.comment_schema import GetCommentCursorResponse, UpdateCommentRequest
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
    summary="댓글 목록 조회(FR-019)",
    description="""
    Responses
    
    성공
    - HTTP_200_OK: 처리 성공
    
    실패
    - HTTP_401_UNAUTHORIZED: 
        - 토큰이 만료되었거나
        - 유효하지 않은 토큰 (형식)일 경우
        
    - HTTP_400_BAD_REQUEST:
        - post_id와 author 쿼리 파라미터가 둘 다 존재하지 않을 때
        - post_id와 author 쿼리 파라미터가 둘 다 존재할 때
        - post_id 파라미터를 보냈는데
          cursor 값이 최상위 부모 댓글이 id가 아닐 때
    
    - HTTP_404_NOT_FOUND:
        - 조회할 구인글 / 사용자 / cursor의 comment가 존재하지 않을 때
      
    - HTTP_422_UNPROCESSABLE_ENTITY(FastAPI server에서 자동 응답): 
        - json type이 잘못되었을 때
        - 쿼리 파라미터 및 request body field의 지정 데이터타입이 아니거나, 지정된 제약조건에 벗어났을 때
    
    - HTTP_500_INTERNAL_SERVER_ERROR: 
        - 예상치 못한 서버 오류(DB 연결 오류, 타입 에러 등 버그)
    """,
    status_code=status.HTTP_200_OK,
)
async def api_get_comment_list(
    post_id: Optional[uuid.UUID] = Query(default=None),
    author: Optional[uuid.UUID] = Query(default=None),
    limit: int = Query(default=20, le=20),
    cursor: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(get_current_user_or_none),
) -> GetCommentCursorResponse:

    if post_id is None and author is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="post_id 나 author 값 중 하나는 필수입니다.",
        )
    if post_id and author:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="post_id 나 author 값 중 하나만 처리가능합니다.",
        )

    current_user_id = None  # 기본적으로 로그인 하지 않은 사용자도 사용 가능
    if current_user:  # Bearer 있으면,
        current_user_id = current_user.id

    try:
        get_comment_cursor_response = await service_get_comment_list(
            db=db,
            post_id=post_id,
            current_user_id=current_user_id,
            author=author,
            limit=limit,
            cursor=cursor,
        )
    except (PostNotFound, UserNotFound, CommentNotFound) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotFirstParentComment as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error in api_change_is_closed_status: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버에 예상치 못한 오류가 발생했습니다.",
        )

    return get_comment_cursor_response


# FR-020: 댓글 수정
@comment_router.patch(
    "/{comment_id}",
    summary="댓글 수정(FR-020)",
    description="""
    Responses
    
    성공
    - HTTP_200_OK: 처리 성공
    
    실패
    - HTTP_401_UNAUTHORIZED: 
        - Bearer token이 없는 경우(로그인 안되어 있는 경우)
        - 토큰이 만료되었거나
        - 유효하지 않은 토큰 형식일 경우
    
    - HTTP_403_FORBIDDEN:
        - 댓글 작성자 본인이 아닐 때
    
    - HTTP_404_NOT_FOUND:
        - 댓글이 존재하지 않을 때
      
    - HTTP_422_UNPROCESSABLE_ENTITY(FastAPI server에서 자동 응답): 
        - json type이 잘못되었을 때
        - 쿼리 파라미터 및 request body field의 지정 데이터타입이 아니거나, 지정된 제약조건에 벗어났을 때
    
    - HTTP_500_INTERNAL_SERVER_ERROR: 
      - 예상치 못한 서버 오류(DB 연결 오류, 타입 에러 등 버그)
    """,
    status_code=status.HTTP_200_OK,
)
async def api_update_comment_content(
    comment_id: uuid.UUID,
    update_comment_request: UpdateCommentRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(get_current_user_required),
) -> None:

    current_user_id = current_user.id

    try:
        await service_update_comment_content(
            db,
            current_user_id,
            comment_id,
            update_comment_request,
        )
    except CommentNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UserNotCommentOwner as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error in api_change_is_closed_status: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버에 예상치 못한 오류가 발생했습니다.",
        )


# FR-021: 댓글 삭제
@comment_router.delete(
    "/{comment_id}",
    summary="댓글 삭제(FR-021)",
    description="""
    Responses
    
    성공
    - HTTP_204_NO_CONTENT: 처리 성공
    
    실패
    - HTTP_401_UNAUTHORIZED: 
        - Bearer token이 없는 경우(로그인 안되어 있는 경우)
        - 토큰이 만료되었거나
        - 유효하지 않은 토큰 형식일 경우
    
    - HTTP_403_FORBIDDEN:
        - 댓글 작성자 본인이 아닐 때
    
    - HTTP_404_NOT_FOUND:
        - 댓글이 존재하지 않을 때
    
    - HTTP_422_UNPROCESSABLE_ENTITY(FastAPI server에서 자동 응답): 
        - json type이 잘못되었을 때
        - 쿼리 파라미터 및 request body field의 지정 데이터타입이 아니거나, 지정된 제약조건에 벗어났을 때
    
    - HTTP_500_INTERNAL_SERVER_ERROR: 
      - 예상치 못한 서버 오류(DB 연결 오류, 타입 에러 등 버그)
    """,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def api_delete_comment(
    comment_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(get_current_user_required),
) -> None:

    current_user_id = current_user.id

    try:
        await service_delete_comment(
            db,
            current_user_id,
            comment_id,
        )
    except CommentNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UserNotCommentOwner as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error in api_change_is_closed_status: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버에 예상치 못한 오류가 발생했습니다.",
        )
