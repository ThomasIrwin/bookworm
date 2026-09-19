"""Schema migrations. Replaces what Flyway and hibernate.ddl-auto=validate guaranteed."""

import asyncio
from typing import Any

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import Connection, make_url, text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool

import app.books.entities
import app.userbooks.entities
import app.users.entities  # noqa: F401  (register every entity on Base.metadata)
from app.database import Base, include_in_migrations
from tests.conftest import alembic_config

pytestmark = pytest.mark.integration

# Verbatim from src/main/resources/db/migration/V1__create_initial_schema.sql.
FLYWAY_V1_SQL = """
CREATE TABLE books (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    description VARCHAR(1000)
);

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    auth0_id VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE user_books (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    book_id BIGINT NOT NULL REFERENCES books(id),
    reading_status VARCHAR(50) NOT NULL
);
"""


def _schema_differences(connection: Connection) -> list[Any]:
    context = MigrationContext.configure(
        connection, opts={"compare_type": True, "include_name": include_in_migrations}
    )
    return list(compare_metadata(context, Base.metadata))


async def _differences(engine: AsyncEngine) -> list[Any]:
    async with engine.connect() as connection:
        return await connection.run_sync(_schema_differences)


async def test_orm_models_match_the_alembic_schema(engine: AsyncEngine) -> None:
    assert await _differences(engine) == []


async def test_upgrade_adopts_a_database_created_by_flyway(database_url: str) -> None:
    baseline_url = make_url(database_url).set(database="flyway_baseline")
    baseline = baseline_url.render_as_string(hide_password=False)

    admin = create_async_engine(database_url, isolation_level="AUTOCOMMIT", poolclass=NullPool)
    async with admin.connect() as connection:
        await connection.execute(text("DROP DATABASE IF EXISTS flyway_baseline"))
        await connection.execute(text("CREATE DATABASE flyway_baseline"))
    await admin.dispose()

    engine = create_async_engine(baseline, poolclass=NullPool)
    try:
        async with engine.begin() as connection:
            for statement in filter(str.strip, FLYWAY_V1_SQL.split(";")):
                await connection.execute(text(statement))
            await connection.execute(text("CREATE TABLE flyway_schema_history (version text)"))
            await connection.execute(
                text("INSERT INTO books (title, author) VALUES ('Existing', 'Data')")
            )

        # Alembic's env.py runs its own event loop, so migrate from a worker thread.
        await asyncio.to_thread(command.upgrade, alembic_config(baseline), "head")

        async with engine.connect() as connection:
            assert (
                await connection.scalar(text("SELECT version_num FROM alembic_version")) == "0001"
            )
            assert await connection.scalar(text("SELECT count(*) FROM books")) == 1
            assert await connection.scalar(
                text("SELECT to_regclass('flyway_schema_history') IS NOT NULL")
            )

        # The ORM models also match the schema Flyway created, not just the one Alembic creates.
        assert await _differences(engine) == []
    finally:
        await engine.dispose()
