from __future__ import annotations

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context as alembic_context
from app.services.suggestions_schema import SUGGESTIONS_METADATA

# this is the Alembic Config object, which provides access to the values
# within the .ini file in use.
config = alembic_context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# target_metadata is used for auto-generating migrations.
target_metadata = SUGGESTIONS_METADATA


def _get_connection_url() -> str:
    overrides = alembic_context.get_x_argument(as_dictionary=True)
    if overrides and "sql-url" in overrides:
        return overrides["sql-url"]

    env_url = os.getenv("ALEMBIC_SQL_CONN_STRING")
    if env_url:
        return env_url

    fallback = config.get_main_option("sqlalchemy.url")
    if fallback and fallback != "postgresql://localhost/postgres":
        return fallback

    raise RuntimeError(
        "Alembic needs ALEMBIC_SQL_CONN_STRING or a -x sql-url override to know which database to target",
    )


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = _get_connection_url()
    alembic_context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with alembic_context.begin_transaction():
        alembic_context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = _get_connection_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        alembic_context.configure(connection=connection, target_metadata=target_metadata)

        with alembic_context.begin_transaction():
            alembic_context.run_migrations()


if alembic_context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
