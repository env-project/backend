# app/services/image_upload.py

import os
import uuid
from app.core.config import settings
from fastapi import HTTPException


async def save_image_file(file) -> str:
    # 파일 확장자 추출
    file_ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(settings.IMAGE_UPLOAD_DIR, filename)

    try:
        # 업로드 디렉토리가 없다면 생성
        os.makedirs(settings.IMAGE_UPLOAD_DIR, exist_ok=True)

        # 파일 저장
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # 업로드된 이미지 URL 생성
        image_url = f"{settings.IMAGE_BASE_URL}/{filename}"
        return image_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing file: {str(e)}")
