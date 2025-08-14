# app/schemas/bookmark.py

from pydantic import BaseModel

class BookmarkResponse(BaseModel):
    message: str
