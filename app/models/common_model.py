# app/models/common.py
from sqlmodel import Field

from .base_model import BaseModel


class Region(BaseModel, table=True):
    __tablename__ = "regions"
    name: str = Field(max_length=50, unique=True, nullable=False)


class Position(BaseModel, table=True):
    __tablename__ = "positions"
    name: str = Field(max_length=50, unique=True, nullable=False)


class Genre(BaseModel, table=True):
    __tablename__ = "genres"
    name: str = Field(max_length=50, unique=True, nullable=False)


class ExperienceLevel(BaseModel, table=True):
    __tablename__ = "experience_levels"
    name: str = Field(max_length=50, unique=True, nullable=False)


class Orientation(BaseModel, table=True):
    __tablename__ = "orientations"
    name: str = Field(max_length=50, unique=True, nullable=False)


class RecruitmentType(BaseModel, table=True):
    __tablename__ = "recruitment_types"
    name: str = Field(max_length=50, unique=True, nullable=False)
