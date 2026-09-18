"""Shared fixtures.

Unit fixtures build a fresh app per test and substitute dependencies, the equivalent of
@WebMvcTest with @MockitoBean. Integration fixtures run PostgreSQL in Testcontainers and roll back
every test, the equivalent of @DataJpaTest.
"""

import os

# Settings require DATABASE_URL. Unit tests never connect; integration tests use the container URL.
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://unused:unused@localhost:1/unused")

from collections.abc import AsyncIterator, Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.auth.dependencies import get_current_auth0_id
from app.main import create_app

SERVER_DIR = Path(__file__).resolve().parent.parent
AUTH0_ID = "auth0|123"


# --- Web layer -------------------------------------------------------------------------------


@pytest.fixture
def app() -> Iterator[FastAPI]:
    application = create_app()
    yield application
    application.dependency_overrides.clear()


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """An unauthenticated client addressing paths relative to the /api/v1 context path."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost:8080/api/v1") as c:
        yield c


@pytest.fixture
def override(app: FastAPI) -> Callable[[Callable[..., Any], Any], None]:
    """Replace a dependency with a fixed value, like @MockitoBean."""

    def _override(dependency: Callable[..., Any], value: Any) -> None:
        app.dependency_overrides[dependency] = lambda: value

    return _override


@pytest.fixture
def authenticate(app: FastAPI) -> Callable[[str], None]:
    """Authenticate requests as the given user, like jwt().jwt(j -> j.claim("sub", ...))."""

    def _authenticate(auth0_id: str = AUTH0_ID) -> None:
        app.dependency_overrides[get_current_auth0_id] = lambda: auth0_id

    return _authenticate


@pytest.fixture
def auth_client(client: AsyncClient, authenticate: Callable[[str], None]) -> AsyncClient:
    authenticate(AUTH0_ID)
    return client


# --- Persistence layer (requires Docker) ----------------------------------------------------


def alembic_config(database_url: str) -> Config:
    config = Config(str(SERVER_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(SERVER_DIR / "migrations"))
    config.set_main_option("sqlalchemy.url", database_url)
    config.attributes["configure_logger"] = False
    return config


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[Any]:
    from testcontainers.community.postgres import PostgresContainer

    with PostgresContainer("postgres:15-alpine", driver="asyncpg") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def database_url(postgres_container: Any) -> str:
    url: str = postgres_container.get_connection_url()
    command.upgrade(alembic_config(url), "head")
    return url


@pytest.fixture
async def engine(database_url: str) -> AsyncIterator[AsyncEngine]:
    # Function-scoped so asyncpg connections never outlive the test's event loop.
    db_engine = create_async_engine(database_url, poolclass=NullPool)
    yield db_engine
    await db_engine.dispose()


@pytest.fixture
async def connection(engine: AsyncEngine) -> AsyncIterator[AsyncConnection]:
    """A connection inside a transaction that is always rolled back after the test."""
    async with engine.connect() as conn:
        transaction = await conn.begin()
        try:
            yield conn
        finally:
            await transaction.rollback()


def session_on(connection: AsyncConnection) -> AsyncSession:
    # Commits inside code under test release a SAVEPOINT; the outer transaction still rolls back.
    return AsyncSession(
        bind=connection, expire_on_commit=False, join_transaction_mode="create_savepoint"
    )


@pytest.fixture
async def session(connection: AsyncConnection) -> AsyncIterator[AsyncSession]:
    async with session_on(connection) as db_session:
        yield db_session
