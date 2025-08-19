import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import (
    Comment,
)
from app.schemas.comment_schema import CommentContentRequest


async def get_comment_by_id(db: AsyncSession, comment_id: uuid.UUID) -> Comment | None:
    """
    comment_id로 댓글을 조회합니다.
    """
    stmt = select(Comment).where(Comment.id == comment_id)
    result = await db.execute(stmt)

    return result.scalars().first()


# FR-019: 댓글 목록 조회
# async def get_my_comment_list(
#     db: AsyncSession,
#     post: RecruitingPost,
#     current_user_id: uuid.UUID,
#     limit: int,
#     cursor: uuid.UUID,
# ) -> list[GetCommentListResponse] | None:
#     # user 정보를 함께 로드하기 위해 selectinload 사용 (N+1 문제 방지)
#     base_query = select(Comment).where(
#         and_(
#             Comment.post_id == post.id,
#             Comment.user_id == current_user_id
#         )
#     )
#
#     if cursor:
#         cursor_subquery = (select(Comment.created_at)
#                            .where(Comment.id == cursor)
#                            .scalar_subquery())
#
#         # 1순위: created_at으로 정렬
#         # 2순위: created_at이 같다면 id로 정렬 (순서 보장)
#         base_query = base_query.where(
#             tuple_(Comment.created_at, Comment.id) < tuple_(cursor_subquery, cursor)
#         )
#
#     final_query = base_query.order_by(
#         Comment.created_at.desc(),
#         Comment.id.desc()
#     ).limit(limit)
#
#     result = await db.execute(final_query)
#     comments = result.scalars().all()
#     if not comments:
#         return None
#
#     comment_list = []
#     for comment in comments:
#         if comment.children:
#             children = await get_child_comment_list(db, post, limit)
#             comment_list.append(
#                 GetCommentListResponse(
#                     comment_id=comment.id,
#                     content=comment.content,
#                     created_at=comment.created_at
#                 )
#             )
#     return comment_list


# async def get_comment_list(
#     db: AsyncSession,
#     post: RecruitingPost,
#         limit:int,
#         cursor:uuid.UUID,
# ) -> list[GetCommentListResponse] | None:


# FR-020: 댓글 수정
async def update_comment_content(
    db: AsyncSession,
    comment: Comment,
    create_comment_request: CommentContentRequest,
) -> None:
    comment.content = create_comment_request.content
    await db.commit()
    await db.refresh(comment)


# FR-021: 댓글 삭제
async def delete_comment_content(
    db: AsyncSession,
    comment: Comment,
) -> None:
    # comment_counts -=

    await db.delete(comment)
    await db.commit()
