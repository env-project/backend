import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import or_, select, tuple_

from app.models import (
    Comment,
    RecruitingPost,
    User,
)
from app.schemas.comment_schema import (
    GetChildCommentResponse,
    GetCommentCursorResponse,
    GetCommentListResponse,
    GetCommentRecruitingResponse,
    UpdateCommentRequest,
)
from app.schemas.recruiting_schema import GetUserProfileResponse


async def get_comment_by_id(db: AsyncSession, comment_id: uuid.UUID) -> Comment | None:
    """
    id로 댓글을 조회합니다.
    """
    stmt = (
        select(Comment)
        .options(
            selectinload(Comment.children),
            selectinload(Comment.post),
        )  # .parent?
        .where(Comment.id == comment_id)
    )
    result = await db.execute(stmt)
    return result.scalars().one_or_none()


# FR-019: 댓글 목록 조회
async def get_comment_list(
    db: AsyncSession,
    post_id: uuid.UUID,
    current_user_id: uuid.UUID,
    author: uuid.UUID,
    limit: int,
    cursor: uuid.UUID,
) -> GetCommentCursorResponse:

    stmt = select(Comment).where(
        or_(Comment.post_id == post_id, Comment.user_id == author)
    )
    # stmt = stmt.where(Comment.parent_comment_id.is_(None)) # 넣어야하나 말아야하나

    if cursor:
        cursor_subquery = (
            select(Comment.created_at).where(Comment.id == cursor).scalar_subquery()
        )
        stmt = stmt.where(
            tuple_(Comment.created_at, Comment.id) <= tuple_(cursor_subquery, cursor)
        )

    stmt = stmt.options(
        selectinload(Comment.post),
        selectinload(Comment.author),
        selectinload(Comment.author).selectinload(User.profile),
        selectinload(Comment.children),
        selectinload(Comment.children).selectinload(Comment.author),
        selectinload(Comment.children)
        .selectinload(Comment.author)
        .selectinload(User.profile),
    )

    final_query = stmt.order_by(Comment.created_at.desc(), Comment.id.desc()).limit(
        limit + 1
    )

    result = await db.execute(final_query)
    comments = result.scalars().all()
    next_cursor = None
    if len(comments) == limit + 1:
        next_cursor = comments[-1].id
        comments = comments[:-1]
    print("조회된 갯수:", len(comments))

    comment_list = []
    if comments:
        for comment in comments:
            if comment.parent_comment_id:
                continue
            comment_dict = comment.model_dump()

            if comment.children:
                comment_dict["children"] = [
                    GetChildCommentResponse(
                        id=child.id,
                        content=child.content,
                        created_at=child.created_at,
                        is_owner=child.user_id == current_user_id,
                        author=GetUserProfileResponse(
                            id=child.user_id,
                            nickname=child.author.nickname,
                            image_url=(
                                child.author.profile.image_url
                                if child.author.profile
                                else None
                            ),
                        ),
                    )
                    for child in comment.children
                ]
            comment_dict["post"] = GetCommentRecruitingResponse.model_validate(
                comment.post
            )
            comment_dict["is_owner"] = comment.user_id == current_user_id
            comment_dict["author"] = GetUserProfileResponse(
                id=comment.author.id,
                nickname=comment.author.nickname,
                image_url=(
                    comment.author.profile.image_url if comment.author.profile else None
                ),
            )
            get_comment = GetCommentListResponse.model_validate(comment_dict)
            comment_list.append(get_comment)

    return GetCommentCursorResponse(
        next_cursor=next_cursor,
        comments=comment_list,
    )


# FR-020: 댓글 수정
async def update_comment_content(
    db: AsyncSession,
    comment: Comment,
    update_comment_request: UpdateCommentRequest,
) -> None:
    comment.content = update_comment_request.content
    await db.commit()


# FR-021: 댓글 삭제
async def delete_comment(
    db: AsyncSession,
    comment: Comment,
    post: RecruitingPost,
) -> None:
    children = len(comment.children)
    post.comments_count -= children + 1

    await db.delete(comment)  # 자식 댓글 delete-orphan
    await db.commit()
