import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models import Position
from app.schemas.frozen_config import FROZEN_CONFIG


class GetRecruitingResponse(BaseModel):
    model_config = FROZEN_CONFIG

    id: uuid.UUID

    title: str
    content: str
    band_name: str | None
    band_composition: str | None
    activity_time: str | None
    contact_info: str | None
    application_method: str | None
    practice_frequency_time: str | None
    # recruitment_type: str
    other_conditions: str | None
    # views_count: int
    # comments_count: int


class PostBookMarkRequest(BaseModel):
    user_id: uuid.UUID
    bookmarked_post_id: uuid.UUID


class CreateRecruitingRequest(BaseModel):
    user_id: uuid.UUID

    title: str
    content: str
    band_name: str | None
    band_composition: str | None
    activity_time: str | None
    contact_info: str | None
    application_method: str | None
    practice_frequency_time: str | None
    other_conditions: str | None

    orientation_id: uuid.UUID
    recruitment_type_id: uuid.UUID

    # region_ids: list[uuid.UUID]
    # genre_ids: list[uuid.UUID]
    positions: list[Position]
    # bookmarks: list[PostBookMarkRequest]

    is_closed: bool = False


##### 공통 #####


class GetUserProfileResponse(BaseModel):
    model_config = FROZEN_CONFIG

    user_id: uuid.UUID
    nickname: str

    image_url: str | None = None  # from Profile


class GetOrientationResponse(BaseModel):
    model_config = FROZEN_CONFIG

    id: uuid.UUID
    name: str


class GetRecruitmentTypeResponse(BaseModel):
    model_config = FROZEN_CONFIG

    id: uuid.UUID
    name: str


class GetRegionResponse(BaseModel):
    model_config = FROZEN_CONFIG

    id: uuid.UUID
    name: str


class GetGenreResponse(BaseModel):
    model_config = FROZEN_CONFIG

    id: uuid.UUID
    name: str


class GetPositionResponse(BaseModel):
    model_config = FROZEN_CONFIG

    position_id: uuid.UUID
    position_name: str
    experienced_level_id: uuid.UUID
    experienced_level_name: str


class UpdatePositionRequest(BaseModel):
    position_id: uuid.UUID
    experienced_level_id: uuid.UUID


##### 공통 끝 #####


# FR-012: 구인글 상세 조회
class GetRecruitingDetailResponse(BaseModel):
    model_config = FROZEN_CONFIG

    id: uuid.UUID
    created_at: datetime

    author: GetUserProfileResponse

    title: str
    content: str

    image_url: str | None = None
    band_name: str | None = None
    band_composition: str | None = None
    activity_time: str | None = None
    contact_info: str | None = None
    application_method: str | None = None
    practice_frequency_time: str | None = None
    other_conditions: str | None = None

    is_closed: bool = False
    is_owner: bool = False
    is_bookmarked: bool = False

    views_count: int = 0
    comments_count: int = 0
    bookmarks_count: int = 0

    orientation: GetOrientationResponse
    recruitment_type: GetRecruitmentTypeResponse

    regions: list[GetRegionResponse] | None = None
    genres: list[GetGenreResponse] | None = None
    positions: list[GetPositionResponse] | None = None


# FR-014: 구인글 작성, FR-015: 구인글 수정
class RecruitingDetailRequest(BaseModel):
    user_id: uuid.UUID

    title: str
    content: str

    image_url: str | None = None
    band_name: str | None = None
    band_composition: str | None = None
    activity_time: str | None = None
    contact_info: str | None = None
    application_method: str | None = None
    practice_frequency_time: str | None = None
    other_conditions: str | None = None

    orientation_id: uuid.UUID
    recruitment_type_id: uuid.UUID

    region_ids: list[uuid.UUID] | None = None
    genre_ids: list[uuid.UUID] | None = None
    positions: list[UpdatePositionRequest] | None = None
