import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.frozen_config import FROZEN_CONFIG
from app.schemas.recruiting_schema import (
    GetUserProfileResponse,
)


# FR-018: 댓글 작성
class CreateCommentRequest(BaseModel):
    content: str
    parent_comment_id: str | None = None


# FR-020: 댓글 수정
class UpdateCommentRequest(BaseModel):
    content: str


class GetCommentRecruitingResponse(BaseModel):
    model_config = FROZEN_CONFIG

    id: uuid.UUID
    title: str


class GetChildCommentResponse(BaseModel):
    model_config = FROZEN_CONFIG

    id: uuid.UUID
    content: str
    created_at: datetime

    is_owner: bool
    author: GetUserProfileResponse


# FR-019: 댓글 목록 조회
class GetCommentListResponse(BaseModel):
    model_config = FROZEN_CONFIG

    id: uuid.UUID
    content: str
    created_at: datetime

    post: GetCommentRecruitingResponse

    is_owner: bool
    author: GetUserProfileResponse

    children: list["GetChildCommentResponse"] | None = None


class GetCommentCursorResponse(BaseModel):
    model_config = FROZEN_CONFIG

    next_cursor: uuid.UUID | None = None
    comments: list[GetCommentListResponse] | None = None
