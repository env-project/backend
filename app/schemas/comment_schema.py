import uuid

from pydantic import BaseModel

from app.schemas.frozen_config import FROZEN_CONFIG
from app.schemas.recruiting_schema import (
    GetUserProfileResponse,
)


# FR-018: 댓글 작성, FR-020: 댓글 수정
class CommentContentRequest(BaseModel):
    content: str
    parent_comment_id: str | None = None


class GetCommentRecruitingResponse(BaseModel):
    model_config = FROZEN_CONFIG

    id: uuid.UUID
    title: str


class GetChildCommentResponse(BaseModel):
    model_config = FROZEN_CONFIG

    id: uuid.UUID
    content: str
    created_at: str

    is_owner: bool = False
    author: GetUserProfileResponse

    children: list["GetChildCommentResponse"] | None = None


# FR-019: 댓글 목록 조회
class GetCommentListResponse(BaseModel):
    model_config = FROZEN_CONFIG

    id: uuid.UUID
    content: str
    created_at: str

    post: GetCommentRecruitingResponse

    is_owner: bool = False
    author: GetUserProfileResponse

    children: list["GetChildCommentResponse"] | None = None