# app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # .env 파일 설정
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # 기존 환경 변수들
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    # 이미지 업로드 관련 환경 변수
    IMAGE_UPLOAD_DIR: str = "./uploaded_images"
    IMAGE_BASE_URL: str = "http://localhost:8000/static/images"  # 상황에 맞게 수정


settings = Settings()
