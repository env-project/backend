# app/schemas/common.py
import uuid

from sqlmodel import SQLModel


class RegionRead(SQLModel):
    id: uuid.UUID
    name: str


class PositionRead(SQLModel):
    id: uuid.UUID
    name: str


class ExperienceLevelRead(SQLModel):
    id: uuid.UUID
    name: str


class PositionWithExperienceRead(SQLModel):
    position: PositionRead
    experience_level: ExperienceLevelRead


class GenreRead(SQLModel):
    id: uuid.UUID
    name: str
