import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.v1.dependencies import (
    get_current_user_or_none,
    get_current_user_required,
)
from app.core.database import get_async_session
from app.exceptions.exceptions import (
    CommentNotFound,
    NotFirstParentComment,
    PostNotFound,
    RecruitingCommentNotMatch,
    UserNotFound,
    UserNotRecruitingPostOwner,
)
from app.schemas.comment_schema import CreateCommentRequest
from app.schemas.enums import IsBookmarked, SortBy
from app.schemas.recruiting_schema import (
    GetRecruitingCursorResponse,
    GetRecruitingDetailResponse,
    RecruitingDetailRequest,
)
from app.services.recruiting_service import (
    service_create_comment,
    service_create_recruiting,
    service_delete_recruiting,
    service_get_recruiting_detail,
    service_get_recruiting_list,
    service_update_recruiting_detail,
    service_update_recruiting_is_closed_status,
)

# 로거 설정 (별도의 설정 파일 필요)
logger = logging.getLogger(__name__)

recruiting_router = APIRouter()  # redirect_slashes=False


# FR-011: 구인글 목록 조회
@recruiting_router.get(
    "",
    description="""
    구인글 목록 조회(FR-011)
    
    성공
    - HTTP_200_OK: 처리 성공
    
    실패
    - HTTP_401_UNAUTHORIZED: 
        - 토큰이 만료되었거나
        - 유효하지 않은 토큰 (형식)일 경우
        
    - HTTP_400_BAD_REQUEST:
        - bookmarks=me 라고 보냈을 때
          Bearer token이 없는 경우(로그인 안되어 있는 경우)
      
    - HTTP_422_UNPROCESSABLE_ENTITY(FastAPI server에서 자동 응답): 
        - json type이 잘못되었을 때
        - 쿼리 파라미터 및 request body field의 지정 데이터타입이 아니거나, 지정된 제약조건에 벗어났을 때
      
    - HTTP_500_INTERNAL_SERVER_ERROR: 
        - 예상치 못한 서버 오류(DB 연결 오류, 타입 에러 등 버그)
    """,
    response_model=GetRecruitingCursorResponse,
    status_code=status.HTTP_200_OK,
)
async def api_get_recruiting(
    limit: Optional[int] = Query(20, le=20),
    cursor: Optional[uuid.UUID] = Query(None),
    author: Optional[uuid.UUID] = Query(None),
    bookmarks: Optional[IsBookmarked] = Query(None),
    search_query: Optional[str] = Query(None),
    orientation: Optional[uuid.UUID] = Query(None),
    experienced_level: Optional[uuid.UUID] = Query(None),
    region_ids: Optional[List[uuid.UUID]] = Query(None),
    position_ids: Optional[List[uuid.UUID]] = Query(None),
    genre_ids: Optional[List[uuid.UUID]] = Query(None),
    sort_by: SortBy = Query(SortBy.LATEST),
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(get_current_user_or_none),
) -> GetRecruitingCursorResponse:

    current_user_id = None  # 기본적으로 로그인 하지 않은 사용자도 사용 가능
    if current_user:  # Bearer 있으면,
        current_user_id = current_user.id
    elif bookmarks:  # 로그인 안되어 있을 때
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str("로그인이 필요한 항목입니다."),
        )

    try:
        get_recruiting_cursor_response = await service_get_recruiting_list(
            db=db,
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
    except UserNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error in api_change_is_closed_status: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버에 예상치 못한 오류가 발생했습니다.",
        )

    return get_recruiting_cursor_response


# FR-014: 구인글 작성
@recruiting_router.post(
    "",
    description="""
    구인글 작성(FR-014)
    
    성공
    - HTTP_201_CREATED: 생성 성공
    
    실패
    - HTTP_401_UNAUTHORIZED: 
        - Bearer token이 없는 경우(로그인 안되어 있는 경우)
        - 토큰이 만료되었거나
        - 유효하지 않은 토큰 (형식)일 경우
        
    - HTTP_400_NOT_FOUND:
	    - title과 content를 보내지 않은 경우: 필수 값
        
    - HTTP_422_UNPROCESSABLE_ENTITY(FastAPI server에서 자동 응답): 
        - json type이 잘못되었을 때
        - 쿼리 파라미터 및 request body field의 지정 데이터타입이 아니거나, 지정된 제약조건에 벗어났을 때
      
    - HTTP_500_INTERNAL_SERVER_ERROR: 
        - 예상치 못한 서버 오류(DB 연결 오류, 타입 에러 등 버그)
    """,
    status_code=status.HTTP_201_CREATED,
)
async def api_create_recruiting(
    create_recruiting_request: RecruitingDetailRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: uuid.UUID = Depends(get_current_user_required),
) -> None:

    if (
        create_recruiting_request.title is None
        or create_recruiting_request.content is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="title과 content는 필수값입니다.",
        )

    current_user_id = current_user.id

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
    
    성공
    - HTTP_200_OK: 처리 성공
    
    실패
    - HTTP_401_UNAUTHORIZED: 
        - 토큰이 만료되었거나
        - 유효하지 않은 토큰 (형식)일 경우
      
    - HTTP_422_UNPROCESSABLE_ENTITY(FastAPI server에서 자동 응답): 
        - json type이 잘못되었을 때
        - 쿼리 파라미터 및 request body field의 지정 데이터타입이 아니거나, 지정된 제약조건에 벗어났을 때
    
    - HTTP_500_INTERNAL_SERVER_ERROR: 
      - 예상치 못한 서버 오류(DB 연결 오류, 타입 에러 등 버그)
    """,
    response_model=GetRecruitingDetailResponse,
    status_code=status.HTTP_200_OK,
)
async def api_get_recruiting_detail(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(get_current_user_or_none),
) -> GetRecruitingDetailResponse:

    current_user_id = None  # 기본적으로 로그인 하지 않은 사용자도 사용 가능
    if current_user:  # Bearer 있으면,
        current_user_id = current_user.id

    try:
        get_recruiting_detail_response = await service_get_recruiting_detail(
            db=db, post_id=post_id, current_user_id=current_user_id
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
    current_user: str = Depends(get_current_user_required),
) -> None:

    current_user_id = current_user.id

    try:
        await service_update_recruiting_detail(
            db=db,
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


# FR-016: 구인글 마감 상태 변경
@recruiting_router.patch(
    "/{post_id}/status",
    description="""
    구인글 마감 상태 변경(FR-016)
    
    성공
    - HTTP_200_OK: 처리 성공
    
    실패
    - HTTP_401_UNAUTHORIZED: 
        - Bearer token이 없는 경우(로그인 안되어 있는 경우)
        - 토큰이 만료되었거나
        - 유효하지 않은 토큰 형식일 경우
    
    - HTTP_403_FORBIDDEN:
        - 작성자 본인이 아닐 때
    
    - HTTP_404_NOT_FOUND:
        - 구인글이 존재하지 않을 때
      
    - HTTP_422_UNPROCESSABLE_ENTITY(FastAPI server에서 자동 응답): 
        - json type이 잘못되었을 때
        - 쿼리 파라미터 및 request body field의 지정 데이터타입이 아니거나, 지정된 제약조건에 벗어났을 때
    
    - HTTP_500_INTERNAL_SERVER_ERROR: 
        - 예상치 못한 서버 오류(DB 연결 오류, 타입 에러 등 버그)
    """,
    status_code=status.HTTP_200_OK,
)
async def api_update_recruiting_is_closed_status(
    post_id: uuid.UUID,
    is_closed: bool,
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(get_current_user_required),
) -> None:

    current_user_id = current_user.id

    try:
        await service_update_recruiting_is_closed_status(
            db=db, post_id=post_id, current_user_id=current_user_id, is_closed=is_closed
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
    
    성공
    - HTTP_204_NO_CONTENT: 처리 성공
    
    실패
    - HTTP_401_UNAUTHORIZED: 
        - Bearer token이 없는 경우(로그인 안되어 있는 경우)
        - 토큰이 만료되었거나
        - 유효하지 않은 토큰 형식일 경우
    
    - HTTP_403_FORBIDDEN:
        - 작성자 본인이 아닐 때
    
    - HTTP_404_NOT_FOUND:
        - 구인글이 존재하지 않을 때
      
    - HTTP_422_UNPROCESSABLE_ENTITY(FastAPI server에서 자동 응답): 
        - json type이 잘못되었을 때
        - 쿼리 파라미터 및 request body field의 지정 데이터타입이 아니거나, 지정된 제약조건에 벗어났을 때
      
    - HTTP_500_INTERNAL_SERVER_ERROR: 
        - 예상치 못한 서버 오류(DB 연결 오류, 타입 에러 등 버그)
    """,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def api_delete_recruiting(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(get_current_user_required),
) -> None:

    current_user_id = current_user.id

    try:
        await service_delete_recruiting(
            db=db, post_id=post_id, current_user_id=current_user_id
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
    
    성공
    - HTTP_201_CREATED: 생성 성공
    
    실패
    - HTTP_401_UNAUTHORIZED: 
        - Bearer token이 없는 경우(로그인 안되어 있는 경우)
        - 토큰이 만료되었거나
        - 유효하지 않은 토큰 형식일 경우
    
    - HTTP_404_NOT_FOUND:
        - 구인글이 존재하지 않을 때
        - 부모 댓글이 존재하지 않을 때
    
    - HTTP_400_BAD_REQUEST:
        - 최상위 부모 댓글이 아닐 때
        - 구인글에 맞는 댓글 id가 아닐 때
      
    - HTTP_422_UNPROCESSABLE_ENTITY(FastAPI server에서 자동 응답): 
        - json type이 잘못되었을 때
        - 쿼리 파라미터 및 request body field의 지정 데이터타입이 아니거나, 지정된 제약조건에 벗어났을 때
    
    - HTTP_500_INTERNAL_SERVER_ERROR: 
        - 예상치 못한 서버 오류(DB 연결 오류, 타입 에러 등 버그)
    """,
    status_code=status.HTTP_201_CREATED,
)
async def api_create_comment(
    post_id: uuid.UUID,
    create_comment_request: CreateCommentRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(get_current_user_required),
) -> None:

    current_user_id = current_user.id

    try:
        await service_create_comment(
            db=db,
            post_id=post_id,
            current_user_id=current_user_id,
            create_comment_request=create_comment_request,
        )
    except (PostNotFound, CommentNotFound) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (NotFirstParentComment, RecruitingCommentNotMatch) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error in api_change_is_closed_status: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버에 예상치 못한 오류가 발생했습니다.",
        )
