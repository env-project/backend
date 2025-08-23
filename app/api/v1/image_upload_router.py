# app/api/v1/image_upload_router.py

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.image_upload_schema import ImageUploadResponse
from app.services.image_upload_service import save_image_file

image_upload_router = APIRouter()


@image_upload_router.post("", response_model=ImageUploadResponse, status_code=201)
async def upload_image(file: UploadFile = File(...)):
    try:
        image_url = await save_image_file(file)
        return {"image_url": image_url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="FILE_STORAGE_ERROR")
