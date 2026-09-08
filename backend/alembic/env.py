from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import asyncio

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

import os
from app.database import Base, engine
from app.config import settings

target_metadata = Base.metadata


def run_migrations_online():
    connectable = engine.sync_engine  # use sync engine for alembic operations if configured

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    raise RuntimeError("Alembic offline mode is not configured in this template")
else:
    run_migrations_online()
