# --- 1. 상단에 추가한 내용 ---
import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

from alembic import context

# Alembic이 테이블 변경사항을 감지할 수 있도록
# 앞으로 만들 모든 SQLModel 모델들을 여기에 import 해야 함
# 예시: from app.models.user import User
# 지금은 비워두거나, 아래처럼 모든 모델을 가져오는 __init__.py를 만들 수 있음
# from app.models import *

# .env 파일을 로드하여 환경 변수를 읽어옴
# 프로젝트 루트의 .env 파일을 찾기 위해 경로를 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# --- 1. 상단에 추가할 내용 끝 ---

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

# --- 2. target_metadata 설정 ---
# SQLModel의 메타데이터를 Alembic의 타겟으로 설정
target_metadata = SQLModel.metadata
# --- 2. target_metadata 설정 끝 ---

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # --- 3. run_migrations_online() 함수 수정 ---
    # .env 파일에서 읽어온 DATABASE_URL을 config에 설정
    db_url_from_env = os.getenv("DATABASE_URL")
    if db_url_from_env:
        config.set_main_option("sqlalchemy.url", db_url_from_env)
    else:
        # .env 파일에 DATABASE_URL이 없는 경우를 대비한 예외 처리
        raise ValueError("DATABASE_URL is not set in the environment variables.")
    # --- 3. run_migrations_online() 함수 수정 끝 ---

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
