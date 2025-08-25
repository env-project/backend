# app/api/v1/image_upload_router.py
import logging

from fastapi import APIRouter, File, HTTPException, UploadFile
from starlette import status

from app.schemas.image_upload_schema import ImageUploadResponse
from app.services.image_upload_service import service_upload_image

image_upload_router = APIRouter()

logger = logging.getLogger(__name__)


@image_upload_router.post(
    "", response_model=ImageUploadResponse, status_code=status.HTTP_201_CREATED
)
async def api_upload_image(file: UploadFile = File(...)) -> ImageUploadResponse:
    try:
        image_url = await service_upload_image(file)
    except Exception as e:
        logger.error(e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버에 예상치 못한 오류가 발생했습니다.",
        )

    return ImageUploadResponse(image_url=image_url)
