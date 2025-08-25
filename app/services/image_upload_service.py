# app/services/image_upload.py
import logging
import os
import uuid

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
from dotenv import load_dotenv
from fastapi import HTTPException, UploadFile


logger = logging.getLogger(__name__)


load_dotenv()  # .env 파일 로드
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("AWS_S3_BUCKET")

# boto3 S3 클라이언트 생성
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION,
)


async def service_upload_image(file: UploadFile) -> str:
    file_ext = file.filename.split(".")[-1]  # 파일 확장자
    signed_filename = f"{uuid.uuid4()}.{file_ext}"  # 중복으로 덮어씌우기 방지
    s3_key = f"uploads/{signed_filename}"

    try:
        s3_client.upload_fileobj(
            file.file,  # file-like object
            S3_BUCKET,
            s3_key,
            ExtraArgs={"ContentType": file.content_type},
        )

        return f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
    except ClientError as e:
        # AWS 권한, 버킷 문제
        logger.error(f"AWS ClientError: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="FILE_STORAGE_ERROR")
    except BotoCoreError as e:
        # 네트워크 또는 boto3 내부 오류
        logger.error(f"BotoCoreError: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="FILE_STORAGE_ERROR")
    except NoCredentialsError as e:
        logger.error(f"NoCredentialsError: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="FILE_STORAGE_ERROR")

    # file_path = os.path.join(settings.IMAGE_UPLOAD_DIR, filename)
    # try:
    #     os.makedirs(settings.IMAGE_UPLOAD_DIR, exist_ok=True)
    #     with open(file_path, "wb") as f:
    #         content = await file.read()
    #         f.write(content)
    #     image_url = f"{settings.IMAGE_BASE_URL}/{filename}"
    #     return image_url
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Error storing file: {str(e)}")
