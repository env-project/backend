# app/models/user.py
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlmodel import Field, Relationship, SQLModel

from .base_model import BaseModel

if TYPE_CHECKING:
    from .bookmark import PostBookmark, UserBookmark
    from .common import Genre, Position, Region
    from .recruiting import Comment, RecruitingPost

# --- M:N 연결 테이블 (Link Tables) ---


class ProfileRegionLink(SQLModel, table=True):
    __tablename__ = "profile_regions"
    profile_id: uuid.UUID = Field(foreign_key="profiles.id", primary_key=True)
    region_id: uuid.UUID = Field(foreign_key="regions.id", primary_key=True)


class ProfilePositionLink(SQLModel, table=True):
    __tablename__ = "profile_positions"
    profile_id: uuid.UUID = Field(foreign_key="profiles.id", primary_key=True)
    position_id: uuid.UUID = Field(foreign_key="positions.id", primary_key=True)
    experience_level_id: uuid.UUID = Field(foreign_key="experience_levels.id")


class ProfileGenreLink(SQLModel, table=True):
    __tablename__ = "profile_genres"
    profile_id: uuid.UUID = Field(foreign_key="profiles.id", primary_key=True)
    genre_id: uuid.UUID = Field(foreign_key="genres.id", primary_key=True)


# --- 주 테이블 (Main Tables) ---

class User(BaseModel, table=True):
    __tablename__ = "users"

    email: Optional[str] = Field(max_length=255, unique=True, index=True)
    password_hash: Optional[str] = Field(default=None)
    nickname: str = Field(max_length=20, unique=True, index=True)
    is_active: bool = Field(default=True)
    bookmark_count: int = Field(default=0, nullable=False)
    last_login_at: Optional[datetime] = Field(default=None)

    login_type: str = Field(
        sa_column=Column(
            ENUM("email", "social", name="login_type_enum", create_type=False),
            nullable=False,
        )
    )

    profile: Optional["Profile"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"uselist": False}
    )
    social_accounts: List["SocialAccount"] = Relationship(back_populates="user")
    recruiting_posts: List["RecruitingPost"] = Relationship(back_populates="author")
    comments: List["Comment"] = Relationship(back_populates="author")
    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="user")

    bookmarks_sent: List["UserBookmark"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "UserBookmark.user_id"},
    )
    bookmarks_received: List["UserBookmark"] = Relationship(
        back_populates="bookmarked_user",
        sa_relationship_kwargs={"foreign_keys": "UserBookmark.bookmarked_user_id"},
    )
    post_bookmarks: List["PostBookmark"] = Relationship(back_populates="user")


class Profile(BaseModel, table=True):
    __tablename__ = "profiles"

    user_id: uuid.UUID = Field(foreign_key="users.id", unique=True)
    image_url: Optional[str] = Field(default=None)
    social_image_url: Optional[str] = Field(default=None)
    is_public: bool = Field(default=True)

    user: "User" = Relationship(back_populates="profile")
    regions: List["Region"] = Relationship(
        back_populates="profiles", link_model=ProfileRegionLink
    )
    positions: List["Position"] = Relationship(
        back_populates="profiles", link_model=ProfilePositionLink
    )
    genres: List["Genre"] = Relationship(
        back_populates="profiles", link_model=ProfileGenreLink
    )


class SocialAccount(BaseModel, table=True):
    __tablename__ = "social_accounts"

    user_id: uuid.UUID = Field(foreign_key="users.id")
    provider: str = Field(
        sa_column=Column(
            ENUM(
                "google",
                "naver",
                "kakao",
                "apple",
                name="social_provider_enum",
                create_type=False,
            ),
            nullable=False,
        )
    )
    provider_id: str = Field(max_length=100)
    email: Optional[str] = Field(max_length=255, default=None)
    is_verified: bool = Field(default=False)
    raw_data: Optional[dict] = Field(default=None, sa_column=Column(JSONB))

    user: "User" = Relationship(back_populates="social_accounts")


class RefreshToken(BaseModel, table=True):
    __tablename__ = "refresh_tokens"

    user_id: uuid.UUID = Field(foreign_key="users.id")
    jti: uuid.UUID = Field(unique=True)
    expired_at: datetime
    is_revoked: bool = Field(default=False)

    user: "User" = Relationship(back_populates="refresh_tokens")
