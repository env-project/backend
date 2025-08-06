# backend/alembic/env.py

# --- 기존 설정 유지 ---
import os
from logging.config import fileConfig

from dotenv import load_dotenv

# SQLAlchemy 2.0에서는 engine_from_config 대신 create_engine을 직접 사용하는 것이 좋습니다.
from sqlalchemy import create_engine, pool
from sqlmodel import SQLModel

from alembic import context

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"), encoding="utf-8")

print("📦 Loaded .env from:", os.path.join(os.getcwd(), ".env"))
print("🔗 DATABASE_URL:", os.getenv("DATABASE_URL"))

print("📦 .env 로드 경로:", os.path.join(BASE_DIR, ".env"))
print("🔗 DATABASE_URL:", os.getenv("DATABASE_URL"))


# --- 기존 설정 유지 끝 ---


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    # ... (이 부분은 수정할 필요 없습니다) ...
    url = os.getenv("DATABASE_URL")  # .ini 대신 os.getenv 사용
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    이 함수를 아래의 내용으로 완전히 교체합니다.
    .env 파일에서 직접 DATABASE_URL을 읽어와 연결을 생성합니다.
    """
    # .env 파일에서 데이터베이스 URL을 가져옵니다.
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        db_url = db_url.strip().strip('"').strip("'")  # 앞뒤 공백과 따옴표 제거
    print("Loaded DATABASE_URL raw:", repr(db_url))

    encoded_bytes = db_url.encode("utf-8", errors="replace")
    print(f"Encoded bytes length: {len(encoded_bytes)}")
    print(f"Byte at position 63: {encoded_bytes[63]} (hex: {encoded_bytes[63]:02x})")

    if len(db_url) > 63:
        print(f"Char at position 63: {db_url[63]} (ord: {ord(db_url[63])})")
    else:
        print("DATABASE_URL is shorter than 64 characters")

    start = max(0, 63 - 5)
    end = min(len(encoded_bytes), 63 + 5)
    print("Bytes around position 63:", encoded_bytes[start:end])

    if not db_url:
        raise ValueError("DATABASE_URL is not set in the environment variables.")

    # SQLAlchemy 2.0 스타일로 직접 엔진을 생성합니다.
    connectable = create_engine(db_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
