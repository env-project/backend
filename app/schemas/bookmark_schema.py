# app/schemas/bookmark_schema.py

import uuid
from datetime import datetime

from pydantic import BaseModel


class BookmarkResponse(BaseModel):
    id: uuid.UUID
    message: str = "북마크가 성공적으로 처리되었습니다."
    created_at: datetime
