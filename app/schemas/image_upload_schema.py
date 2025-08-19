# app/schemas/image_upload.py

from pydantic import BaseModel


class ImageUploadResponse(BaseModel):
    image_url: str

    class Config:
        from_attributes = True  # "orm_mode = True" has been deprecated
