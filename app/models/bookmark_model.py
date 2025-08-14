# app/models/bookmark_model.py
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from .base_model import BaseModel

if TYPE_CHECKING:
    from .recruiting_model import RecruitingPost
    from .user_model import User


# 여기에 하나 추가해야 됨(row)
# 해당되는 유저의 bookmark count auto-increment(+1)
# 삭제할 때는 row부터 > 그 다음 -1
class UserBookmark(BaseModel, table=True):
    __tablename__ = "user_bookmarks"
    __table_args__ = (
        UniqueConstraint("user_id", "bookmarked_user_id", name="uq_user_bookmark"),
    )

    user_id: uuid.UUID = Field(foreign_key="users.id")
    bookmarked_user_id: uuid.UUID = Field(foreign_key="users.id")
    user: "User" = Relationship(
        back_populates="bookmarks_sent",
        sa_relationship_kwargs={"foreign_keys": "[UserBookmark.user_id]"},
    )
    bookmarked_user: "User" = Relationship(
        back_populates="bookmarks_received",
        sa_relationship_kwargs={"foreign_keys": "[UserBookmark.bookmarked_user_id]"},
    )


class PostBookmark(BaseModel, table=True):
    __tablename__ = "post_bookmarks"
    __table_args__ = (
        UniqueConstraint("user_id", "bookmarked_post_id", name="uq_post_bookmark"),
    )

    user_id: uuid.UUID = Field(foreign_key="users.id")
    bookmarked_post_id: uuid.UUID = Field(foreign_key="recruiting_posts.id")

    user: "User" = Relationship(back_populates="post_bookmarks")
    post: "RecruitingPost" = Relationship(back_populates="bookmarks")
