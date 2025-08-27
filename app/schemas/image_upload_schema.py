# app/schemas/image_upload.py

from pydantic import BaseModel

from app.schemas.frozen_config import FROZEN_CONFIG


class ImageUploadRequest(BaseModel):
    filename: str


class ImageUploadResponse(BaseModel):
    model_config = FROZEN_CONFIG

    image_url: str

    # class Config:
    #     from_attributes = True  # "orm_mode = True" has been deprecated
