# app/schemas/user.py
import uuid
from typing import List

from sqlmodel import SQLModel


# --- 공통 내부 모델 ---
class RegionRead(SQLModel):
    id: uuid.UUID
    name: str


class PositionWithExperienceRead(SQLModel):
    position: RegionRead
    experience_level: RegionRead


class GenreRead(SQLModel):
    id: uuid.UUID
    name: str


class ProfileRead(SQLModel):
    image_url: str | None
    is_public: bool
    regions: List[RegionRead]
    positions: List[PositionWithExperienceRead]
    genres: List[GenreRead]


# --- Request Schemas ---


class UserCreate(SQLModel):
    email: str
    password: str
    nickname: str


# --- Response Schemas ---


class UserRead(SQLModel):
    id: uuid.UUID
    email: str
    nickname: str


# 내 정보 조회를 위한 응답 모델
class UserReadWithProfile(UserRead):
    profile: ProfileRead | None
