# app/models/common.py
from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship

from .base_model import BaseModel
from .recruiting_model import (
    RecruitingPostGenreLink,
    RecruitingPostPositionLink,
    RecruitingPostRegionLink,
)
from .user_model import ProfileGenreLink, ProfilePositionLink, ProfileRegionLink

# 순환 참조를 피하기 위해 타입 검사 시에만 import
if TYPE_CHECKING:
    from .recruiting_model import RecruitingPost
    from .user_model import Profile


class Region(BaseModel, table=True):
    __tablename__ = "regions"
    name: str = Field(max_length=50, unique=True, nullable=False)

    profiles: List["Profile"] = Relationship(
        back_populates="regions", link_model=ProfileRegionLink
    )
    recruiting_posts: List["RecruitingPost"] = Relationship(
        back_populates="regions", link_model=RecruitingPostRegionLink
    )


class Position(BaseModel, table=True):
    __tablename__ = "positions"
    name: str = Field(max_length=50, unique=True, nullable=False)

    profiles: List["Profile"] = Relationship(
        back_populates="positions", link_model=ProfilePositionLink
    )
    recruiting_posts: List["RecruitingPost"] = Relationship(
        back_populates="positions", link_model=RecruitingPostPositionLink
    )


class Genre(BaseModel, table=True):
    __tablename__ = "genres"
    name: str = Field(max_length=50, unique=True, nullable=False)

    profiles: List["Profile"] = Relationship(
        back_populates="genres", link_model=ProfileGenreLink
    )
    recruiting_posts: List["RecruitingPost"] = Relationship(
        back_populates="genres", link_model=RecruitingPostGenreLink
    )


class ExperienceLevel(BaseModel, table=True):
    __tablename__ = "experience_levels"
    name: str = Field(max_length=50, unique=True, nullable=False)


class Orientation(BaseModel, table=True):
    __tablename__ = "orientations"
    name: str = Field(max_length=50, unique=True, nullable=False)


class RecruitmentType(BaseModel, table=True):
    __tablename__ = "recruitment_types"
    name: str = Field(max_length=50, unique=True, nullable=False)
