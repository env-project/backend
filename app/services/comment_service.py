import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.comment_crud import (
    delete_comment,
    get_comment_by_id,
    get_comment_list,
    update_comment_content,
)
from app.crud.recruiting_crud import get_recruiting_by_id, get_user_by_id
from app.exceptions.exceptions import (
    CommentNotFound,
    PostNotFound,
    UserNotCommentOwner,
    UserNotFound,
)
from app.schemas.comment_schema import (
    CreateCommentRequest,
    GetCommentCursorResponse,
)


# FR-019: 댓글 목록 조회
async def service_get_comment_list(
    db: AsyncSession,
    post_id: uuid.UUID,
    current_user_id: uuid.UUID,
    author: uuid.UUID,
    limit: int,
    cursor: uuid.UUID,
) -> GetCommentCursorResponse:

    if post_id:
        post = await get_recruiting_by_id(db, post_id)
        if not post:
            raise PostNotFound()
    if author:
        user = await get_user_by_id(db, author)
        if not user:
            raise UserNotFound()

    return await get_comment_list(db, post_id, current_user_id, author, limit, cursor)


# FR-020: 댓글 수정
async def service_update_comment_content(
    db: AsyncSession,
    current_user_id: uuid.UUID,
    comment_id: uuid.UUID,
    update_comment_request: CreateCommentRequest,
) -> None:

    comment = await get_comment_by_id(db, comment_id)
    if not comment:
        raise CommentNotFound()

    # comment 작성자 본인 여부 확인
    if current_user_id != comment.user_id:
        raise UserNotCommentOwner()

    # 댓글이 존재하고,
    # 본인의 댓글이라면
    # 댓글 수정
    await update_comment_content(db, comment, update_comment_request)


# FR-021: 댓글 삭제
async def service_delete_comment(
    db: AsyncSession,
    current_user_id: uuid.UUID,
    comment_id: uuid.UUID,
) -> None:

    comment = await get_comment_by_id(db, comment_id)
    if not comment:
        raise CommentNotFound()

    # comment 작성자 본인 여부 확인
    if current_user_id != comment.user_id:
        raise UserNotCommentOwner()

    post = await get_recruiting_by_id(db, comment.post_id)

    # 댓글이 존재하고,
    # 본인의 댓글이라면
    # 댓글 삭제
    await delete_comment(db, comment, post)
