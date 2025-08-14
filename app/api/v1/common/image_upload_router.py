# app/api/v1/common/image_upload.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.image_upload_service import save_image_file
from app.schemas.image_upload_schema import ImageUploadResponse

router = APIRouter()


@router.post("/", response_model=ImageUploadResponse, status_code=201)
async def upload_image(file: UploadFile = File(...)):
    try:
        image_url = await save_image_file(file)
        return {"image_url": image_url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="FILE_STORAGE_ERROR")