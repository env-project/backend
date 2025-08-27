import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.frozen_config import FROZEN_CONFIG

##### 공통 시작 #####


class GetUserProfileResponse(BaseModel):
    model_config = FROZEN_CONFIG

    id: uuid.UUID
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


class PositionRequest(BaseModel):
    position_id: uuid.UUID
    experienced_level_id: uuid.UUID


##### 공통 끝 #####


# FR-011: 구인글 목록 조회
class GetRecruitingListResponse(BaseModel):
    model_config = FROZEN_CONFIG

    id: uuid.UUID
    author: GetUserProfileResponse | None = None

    title: str

    is_closed: bool
    created_at: datetime

    is_owner: bool
    is_bookmarked: bool

    views_count: int
    comments_count: int
    bookmarks_count: int

    ## optionals start
    orientation: GetOrientationResponse | None = None
    recruitment_type: GetRecruitmentTypeResponse | None = None

    regions: list[GetRegionResponse] | None = None
    genres: list[GetGenreResponse] | None = None
    positions: list[GetPositionResponse] | None = None


class GetRecruitingCursorResponse(BaseModel):
    model_config = FROZEN_CONFIG

    next_cursor: uuid.UUID | None = None
    posts: list[GetRecruitingListResponse] | None = None


# FR-012: 구인글 상세 조회
class GetRecruitingDetailResponse(BaseModel):
    model_config = FROZEN_CONFIG

    id: uuid.UUID
    author: GetUserProfileResponse | None = None

    title: str
    content: str

    is_closed: bool
    created_at: datetime

    is_owner: bool
    is_bookmarked: bool

    views_count: int
    comments_count: int
    bookmarks_count: int

    ## optionals start

    image_url: str | None = None
    band_name: str | None = None
    band_composition: str | None = None
    activity_time: str | None = None
    contact_info: str | None = None
    application_method: str | None = None
    practice_frequency_time: str | None = None
    other_conditions: str | None = None

    orientation: GetOrientationResponse | None = None
    recruitment_type: GetRecruitmentTypeResponse | None = None

    regions: list[GetRegionResponse] | None = None
    genres: list[GetGenreResponse] | None = None
    positions: list[GetPositionResponse] | None = None


# FR-014: 구인글 작성, FR-015: 구인글 수정
class RecruitingDetailRequest(BaseModel):
    title: str | None = None
    content: str | None = None

    image_url: str | None = None
    band_name: str | None = None
    band_composition: str | None = None
    activity_time: str | None = None
    contact_info: str | None = None
    application_method: str | None = None
    practice_frequency_time: str | None = None
    other_conditions: str | None = None

    orientation_id: uuid.UUID | None = None
    recruitment_type_id: uuid.UUID | None = None

    region_ids: list[uuid.UUID] | None = None
    genre_ids: list[uuid.UUID] | None = None
    positions: list[PositionRequest] | None = None
