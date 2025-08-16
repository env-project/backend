import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from starlette import status

from app.core.database import get_async_session
from app.exceptions.exceptions import PostNotFound
from app.models import RecruitingPost
from app.schemas.recruiting_schema import (
    GetRecruitingDetailResponse,
    GetRecruitingResponse,
    RecruitingDetailRequest,
)
from app.services.recruiting_service import (
    service_create_recruiting,
    service_delete_recruiting,
    service_get_recruiting_detail,
    service_update_recruiting_detail,
    service_update_recruiting_is_closed_status,
)

# 로거 설정 (별도의 설정 파일 추천)
logger = logging.getLogger(__name__)

recruiting_router = APIRouter(
    prefix="/v1/recruiting-posts", tags=["recruiting"], redirect_slashes=False
)


@recruiting_router.get(
    "",
    description="""
    다양한 조건으로 필터링/정렬된 구인글 목록을 조회합니다.
    author=me 파라미터를 통해 '내가 작성한 구인글' 조회가 가능합니다.

    Args:
        create_recruiting_request(CreateRecruitingRequest): 구인글 생성 요청 데이터

    Returns:
        GetRecruitingResponse
        HTTP_201_CREATED: 생성 성공 시,
        HTTP_ : 생성 실패 시, msg와 함께 나갑니다.
    """,
    response_model=list[GetRecruitingResponse],
)
async def api_get_recruiting(
    limit: int = Query(default=10, le=10),
    cursor: int = Query(default=0),
    db: AsyncSession = Depends(get_async_session),
) -> list[GetRecruitingResponse]:

    # 값이 틀리면 400 error
    result = await db.execute(select(RecruitingPost).limit(limit))
    posts = result.scalars().all()  # list[RecruitingPost]

    validated_posts = [
        GetRecruitingResponse.model_validate(post.__dict__) for post in posts
    ]

    return validated_posts


# FR-014: 구인글 작성
@recruiting_router.post(
    "",
    description="""
    로그인한 사용자가 새로운 구인글을 생성합니다.

    Args:
        RecruitingDetailRequest: 생성할 구인글의 필드 내용을 담는 객체

    Returns:
        성공
        - HTTP_201_CREATED: 생성 성공

        실패 (with specific error msg)
        - HTTP_401_UNAUTHORIZED: 
            - 아마도...? Error Code는 다를수도 있습니다.
            - JWT에서 자동으로 에러 응답 예상(아직 Auth쪽 구현이 안되었습니다.)
            - JWT 구현 후 가능
        - HTTP_404_NOT_FOUND: 구인글이 존재하지 않을 때
        - HTTP_422_UNPROCESSABLE_ENTITY: 
            - wrong json type
            - FastAPI server에서 자동 에러 응답
        - HTTP_500_INTERNAL_SERVER_ERROR: 예상치 못한 서버 오류(DB 연결 오류, 타입 에러 등 버그)
    """,
    status_code=status.HTTP_201_CREATED,
)
async def api_create_recruiting(
    create_recruiting_request: RecruitingDetailRequest,
    db: AsyncSession = Depends(get_async_session),
) -> None:
    # Permission 추가 (본인이 작성한 구인글인지 여부 확인)
    # user_id 여기서 받아야함.

    try:
        await service_create_recruiting(db, create_recruiting_request)
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

    await db.close()


# FR-012: 구인글 상세 조회
@recruiting_router.get(
    "/{post_id}",
    description="""
    특정 구인글의 상세 정보를 조회합니다.

    Args:

    Returns:
        GetRecruitingDetailResponse: 구인글의 상세 내용을 담는 객체

        성공
        - HTTP_200_OK: 처리 성공

        실패 (with specific error msg)
        - HTTP_401_UNAUTHORIZED: 
            - 아마도...? Error Code는 다를수도 있습니다.
            - JWT에서 자동으로 에러 응답 예상(아직 Auth쪽 구현이 안되었습니다.)
            - JWT 구현 후 가능
        - HTTP_404_NOT_FOUND: 구인글이 존재하지 않을 때
        - HTTP_422_UNPROCESSABLE_ENTITY: 
            - wrong json type
            - FastAPI server에서 자동 에러 응답
        - HTTP_500_INTERNAL_SERVER_ERROR: 예상치 못한 서버 오류(DB 연결 오류, 타입 에러 등 버그)
    """,
    status_code=status.HTTP_200_OK,
)
async def api_get_recruiting_detail(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
) -> GetRecruitingDetailResponse:

    # Permission 추가 (본인이 작성한 구인글인지 여부 확인)
    # user_id 여기서 받아야함.

    try:
        get_recruiting_detail_response = await service_get_recruiting_detail(
            db, post_id=post_id
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

    await db.close()
    return get_recruiting_detail_response


# FR-015: 구인글 수정
@recruiting_router.patch(
    "/{post_id}",
    description="""
    자신이 작성한 구인글의 내용을 수정합니다.

    Args:
        RecruitingDetailRequest: 구인글에서 수정할 필드를 담는 객체

    Returns:
        성공
        - HTTP_200_OK: 처리 성공

        실패 (with specific error msg)
        - HTTP_401_UNAUTHORIZED: 
            - 아마도...? Error Code는 다를수도 있습니다.
            - JWT에서 자동으로 에러 응답 예상(아직 Auth쪽 구현이 안되었습니다.)
            - JWT 구현 후 가능
        - HTTP_404_NOT_FOUND: 구인글이 존재하지 않을 때
        - HTTP_422_UNPROCESSABLE_ENTITY: 
            - wrong json type
            - FastAPI server에서 자동 에러 응답
        - HTTP_500_INTERNAL_SERVER_ERROR: 예상치 못한 서버 오류(DB 연결 오류, 타입 에러 등 버그)
    """,
    status_code=status.HTTP_200_OK,
)
async def api_update_recruiting_detail(
    post_id: uuid.UUID,
    update_recruiting_detail_request: RecruitingDetailRequest,
    db: AsyncSession = Depends(get_async_session),
) -> None:

    # Permission 추가 (본인이 작성한 구인글인지 여부 확인)

    try:
        await service_update_recruiting_detail(
            db,
            post_id=post_id,
            update_recruiting_detail_request=update_recruiting_detail_request,
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

    await db.close()


# FR-016: 구인글 마감 여부 변경
@recruiting_router.patch(
    "/{post_id}/status",
    description="""
    자신이 작성한 구인글의 마감 상태(is_closed)를 변경합니다.

    Args:
        is_closed(bool): 변경할 마감 상태

    Returns:
        UpdateRecruitingIsClosedResponse: 구인글의 id와 is_closed 변경 내용을 담는 객체

        성공
        - HTTP_200_OK: 처리 성공

        실패 (with specific error msg)
        - HTTP_401_UNAUTHORIZED: 
            - 아마도...? Error Code는 다를수도 있습니다.
            - JWT에서 자동으로 에러 응답 예상(아직 Auth쪽 구현이 안되었습니다.)
            - JWT 구현 후 가능
        - HTTP_404_NOT_FOUND: 구인글이 존재하지 않을 때
        - HTTP_422_UNPROCESSABLE_ENTITY: 
            - Not valid query param / wrong json type
            - FastAPI server에서 자동 에러 응답
        - HTTP_500_INTERNAL_SERVER_ERROR: 예상치 못한 서버 오류(DB 연결 오류, 타입 에러 등 버그)
    """,
    status_code=status.HTTP_200_OK,
)
async def api_update_recruiting_is_closed_status(
    post_id: uuid.UUID,
    is_closed: bool,
    db: AsyncSession = Depends(get_async_session),
) -> None:

    # Permission 추가 (본인이 작성한 구인글인지 여부 확인)

    try:
        await service_update_recruiting_is_closed_status(
            db, post_id=post_id, is_closed=is_closed
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

    await db.close()


# FR-017: 구인글 삭제
@recruiting_router.delete(
    "/{post_id}",
    description="""
    자신이 작성한 구인글을 삭제합니다.

    Args:

    Returns:
        성공
        - HTTP_204_NO_CONTENT: 처리 성공

        실패 (with specific error msg)
        - HTTP_401_UNAUTHORIZED: 
            - 아마도...? Error Code는 다를수도 있습니다.
            - JWT에서 자동으로 에러 응답 예상(아직 Auth쪽 구현이 안되었습니다.)
            - JWT 구현 후 가능
        - HTTP_404_NOT_FOUND: 구인글이 존재하지 않을 때
        - HTTP_422_UNPROCESSABLE_ENTITY: 
            - wrong json type
            - FastAPI server에서 자동 에러 응답
        - HTTP_500_INTERNAL_SERVER_ERROR: 예상치 못한 서버 오류(DB 연결 오류, 타입 에러 등 버그)
    """,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def api_delete_recruiting(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
) -> None:

    # Permission 추가 (본인이 작성한 구인글인지 여부 확인)

    try:
        await service_delete_recruiting(db, post_id=post_id)
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

    await db.close()
