"""Async SQLAlchemy engine and request-scoped sessions."""

from collections.abc import AsyncIterator, Mapping
from functools import lru_cache
from typing import Final

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings


class Base(DeclarativeBase):
    pass


# Tables in the database that these models do not own: Flyway's history from the Java service.
UNMANAGED_TABLES: Final = frozenset({"flyway_schema_history"})


def include_in_migrations(
    name: str | None, type_: str, parent_names: Mapping[str, str | None]
) -> bool:
    """Alembic include_name hook that stops autogenerate from dropping unmanaged tables."""
    return not (type_ == "table" and name in UNMANAGED_TABLES)


@lru_cache
def get_engine() -> AsyncEngine:
    return create_async_engine(get_settings().database_url, pool_pre_ping=True)


@lru_cache
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(), expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """One session per request.

    Services own their transaction boundaries and commit explicitly. Closing the session rolls
    back anything left uncommitted, so a request that raises never persists partial work.
    """
    async with get_sessionmaker()() as session:
        yield session
