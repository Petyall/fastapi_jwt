import sys

from pathlib import Path
from alembic import context
from sqlalchemy import pool
from logging.config import fileConfig
from sqlalchemy import engine_from_config

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from config import settings
from models import Base

import models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

if settings.DB_TYPE == "postgresql":
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("asyncpg", "psycopg2"))
elif settings.DB_TYPE == "sqlite":
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("+aiosqlite", ""))
else:
    raise RuntimeError("Неподдерживаемый тип базы данных")

target_metadata = Base.metadata

def run_migrations_offline() -> None:
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
    configuration = config.get_section(config.config_ini_section)
    if settings.DB_TYPE == "postgresql":
        configuration["sqlalchemy.url"] = settings.DATABASE_URL.replace("asyncpg", "psycopg2")
    elif settings.DB_TYPE == "sqlite":
        configuration["sqlalchemy.url"] = settings.DATABASE_URL.replace("+aiosqlite", "")
    else:
        raise RuntimeError("Неподдерживаемый тип базы данных")

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
