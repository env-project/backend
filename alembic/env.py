# alembic/env.py
import asyncio
import os
import platform
import sys
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlmodel import SQLModel

from app.core.config import settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.models import bookmark, common, recruiting, user  # noqa

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    url = str(settings.DATABASE_URL)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = create_async_engine(str(settings.DATABASE_URL))
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
