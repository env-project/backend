# app/schemas/profile.py
import uuid
from typing import List, Optional

from sqlmodel import SQLModel

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
# (응답 스키마는 user.py에서 UserReadWithProfile로 통합되어 있음.)
