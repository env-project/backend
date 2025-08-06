# app/models/base_model.py
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,  # 실제로는 DB의 server_default='uuid_generate_v7()'로 설정됨
        primary_key=True,
        index=True,
        nullable=False,
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Optional[datetime] = Field(
        default=None, sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)}
    )
