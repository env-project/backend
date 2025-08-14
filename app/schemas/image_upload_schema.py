# app/schemas/image_upload.py

from pydantic import BaseModel


class ImageUploadResponse(BaseModel):
    image_url: str

    class Config:
        orm_mode = True