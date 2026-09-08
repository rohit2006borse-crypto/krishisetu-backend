from logging.config import fileConfig
import asyncio
from sqlalchemy import pool
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

from app.database import Base, engine
from app.config import settings

# add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_online():
    """Run migrations in 'online' mode for async engine."""
    connectable = engine

    async def do_run():
        async with connectable.connect() as connection:
            await connection.run_sync(run_migrations)

    def run_migrations(connection):
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()

    asyncio.run(do_run())


if context.is_offline_mode():
    raise RuntimeError("Alembic offline mode is not configured in this template")
else:
    run_migrations_online()
