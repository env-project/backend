import uuid
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from sqlalchemy import text
from sqlmodel import Field, SQLModel

KST = ZoneInfo("Asia/Seoul")


class BaseModel(SQLModel):
    id: Optional[uuid.UUID] = Field(
        default=None,
        primary_key=True,
        nullable=False,
        sa_column_kwargs={"server_default": text("uuid_generate_v7()")},
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(KST),
        nullable=False,
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={"onupdate": lambda: datetime.now(KST)},
    )
