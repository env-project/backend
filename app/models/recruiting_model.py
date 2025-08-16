# app/models/recruiting.py
import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from .base_model import BaseModel

if TYPE_CHECKING:
    from .bookmark_model import PostBookmark
    from .common_model import Genre, Position, Region
    from .user_model import User

# --- M:N 연결 테이블 (Link Tables) ---


class RecruitingPostRegionLink(SQLModel, table=True):
    __tablename__ = "recruiting_post_regions"
    post_id: uuid.UUID = Field(foreign_key="recruiting_posts.id", primary_key=True)
    region_id: uuid.UUID = Field(foreign_key="regions.id", primary_key=True)


class RecruitingPostGenreLink(SQLModel, table=True):
    __tablename__ = "recruiting_post_genres"
    post_id: uuid.UUID = Field(foreign_key="recruiting_posts.id", primary_key=True)
    genre_id: uuid.UUID = Field(foreign_key="genres.id", primary_key=True)


class RecruitingPostPositionLink(SQLModel, table=True):
    __tablename__ = "recruiting_post_positions"
    post_id: uuid.UUID = Field(foreign_key="recruiting_posts.id", primary_key=True)
    position_id: uuid.UUID = Field(foreign_key="positions.id", primary_key=True)
    desired_experience_level_id: uuid.UUID = Field(foreign_key="experience_levels.id")


# --- 주 테이블 (Main Tables) ---


class RecruitingPost(BaseModel, table=True):
    __tablename__ = "recruiting_posts"

    user_id: uuid.UUID = Field(foreign_key="users.id")
    title: str = Field(max_length=255)
    content: str
    band_name: Optional[str] = Field(max_length=100, default=None)
    band_composition: Optional[str] = Field(default=None)
    activity_time: Optional[str] = Field(max_length=100, default=None)
    orientation_id: uuid.UUID = Field(foreign_key="orientations.id")
    contact_info: Optional[str] = Field(max_length=255, default=None)
    application_method: Optional[str] = Field(default=None)
    practice_frequency_time: Optional[str] = Field(max_length=100, default=None)
    recruitment_type_id: uuid.UUID = Field(foreign_key="recruitment_types.id")
    other_conditions: Optional[str] = Field(default=None)
    views_count: int = Field(default=0)
    comments_count: int = Field(default=0)
    bookmarks_count: int = Field(default=0)
    is_closed: bool = Field(default=False)

    author: "User" = Relationship(back_populates="recruiting_posts")
    comments: List["Comment"] = Relationship(back_populates="post")

    regions: List["Region"] = Relationship(
        back_populates="recruiting_posts", link_model=RecruitingPostRegionLink
    )
    genres: List["Genre"] = Relationship(
        back_populates="recruiting_posts", link_model=RecruitingPostGenreLink
    )
    positions: List["Position"] = Relationship(
        back_populates="recruiting_posts", link_model=RecruitingPostPositionLink
    )

    bookmarks: List["PostBookmark"] = Relationship(back_populates="post")


class Comment(BaseModel, table=True):
    __tablename__ = "comments"

    post_id: uuid.UUID = Field(foreign_key="recruiting_posts.id")
    user_id: uuid.UUID = Field(foreign_key="users.id")
    content: str
    parent_comment_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="comments.id"
    )
    path: Optional[str] = Field(max_length=255, default=None, index=True)
    is_deleted: bool = Field(default=False)

    post: "RecruitingPost" = Relationship(back_populates="comments")
    author: "User" = Relationship(back_populates="comments")
    parent: Optional["Comment"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": lambda: [Comment.id]},
    )
    children: List["Comment"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
