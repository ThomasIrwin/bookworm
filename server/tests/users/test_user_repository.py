"""Ports UserRepositoryTest (@DataJpaTest with a Testcontainers PostgreSQL)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.entities import User
from app.users.repository import UserRepository

pytestmark = pytest.mark.integration


@pytest.fixture
def user_repository(session: AsyncSession) -> UserRepository:
    return UserRepository(session)


async def test_find_by_auth0_id_returns_user_when_exists(user_repository: UserRepository) -> None:
    user = User()
    user.auth0_id = "auth0|abc"
    await user_repository.save(user)

    result = await user_repository.find_by_auth0_id("auth0|abc")

    assert result is not None
    assert result.auth0_id == "auth0|abc"


async def test_find_by_auth0_id_returns_empty_when_not_exists(
    user_repository: UserRepository,
) -> None:
    result = await user_repository.find_by_auth0_id("auth0|doesnotexist")

    assert result is None


async def test_upsert_user_inserts_new_user_and_returns_non_zero(
    user_repository: UserRepository,
) -> None:
    result = await user_repository.upsert_user("auth0|newuser")

    assert result == 1
    assert await user_repository.find_by_auth0_id("auth0|newuser") is not None


async def test_upsert_user_does_not_duplicate_existing_user_and_returns_zero(
    user_repository: UserRepository,
) -> None:
    existing_user_auth0_id = "auth0|existing"

    await user_repository.upsert_user(existing_user_auth0_id)

    result = await user_repository.upsert_user(existing_user_auth0_id)

    assert result == 0
    users = await user_repository.find_all()
    assert sum(1 for u in users if u.auth0_id == existing_user_auth0_id) == 1
