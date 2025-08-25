# app/schemas/profile.py
import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import SQLModel

from app.models.user_model import ProfilePositionLink

# from app.schemas.common import ExperienceLevelRead, PositionRead
from .common import ExperienceLevelRead, GenreRead, PositionRead, RegionRead

if TYPE_CHECKING:
    from app.models.user_model import ProfilePositionLink


# --- Request Schemas ---
class PositionPayload(SQLModel):
    position_id: uuid.UUID
    experience_level_id: uuid.UUID


class ProfileUpdate(SQLModel):
    image_url: Optional[str] = None
    is_public: Optional[bool] = None
    region_ids: Optional[List[uuid.UUID]] = None
    positions: Optional[List[PositionPayload]] = None
    genre_ids: Optional[List[uuid.UUID]] = None


# --- Response Schemas ---


class PositionWithExperienceRead(SQLModel):
    position: Optional[PositionRead] = None
    experience_level: Optional[ExperienceLevelRead] = None

    @classmethod
    def from_link(cls, link: ProfilePositionLink):
        return cls(position=link.position, experience_level=link.experience_level)


class ProfileListRead(SQLModel):
    user_id: uuid.UUID
    email: str
    nickname: str
    image_url: str | None
    is_bookmarked: bool
    regions: List[RegionRead]
    positions: List[PositionWithExperienceRead]
    genres: List[GenreRead]


class ProfileListResponse(SQLModel):
    next_cursor: str | None
    profiles: List[ProfileListRead]


class ProfileDetailRead(SQLModel):
    email: str
    nickname: str
    image_url: Optional[str] = None
    is_public: bool
    is_bookmarked: bool
    regions: List[RegionRead]
    positions: Optional[List[PositionWithExperienceRead]] = []
    genres: List[GenreRead]
