from pydantic_settings import BaseSettings, SettingsConfigDict

# from dotenv import load_dotenv
# import os

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# load_dotenv(os.path.join(BASE_DIR, ".env"), encoding="utf-8")


class Settings(BaseSettings):
    # .env 파일을 읽어오도록 설정
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # .env 파일에 정의된 변수들을 타입과 함께 선언
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    image_upload_dir: str
    image_base_url: str

    # 이미지 업로드 관련 환경 변수
    IMAGE_UPLOAD_DIR: str = "./uploaded_images"
    IMAGE_BASE_URL: str = "http://localhost:8000/static/images"  # 상황에 맞게 수정


# 설정 객체 생성
settings = Settings()
