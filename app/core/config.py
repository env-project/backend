from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # .env 파일을 읽어오도록 설정
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # .env 파일에 정의된 변수들을 타입과 함께 선언
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int


# 설정 객체 생성
settings = Settings()
