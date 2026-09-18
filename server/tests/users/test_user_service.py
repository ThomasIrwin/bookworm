"""Ports UserServiceTest."""

from unittest.mock import MagicMock, create_autospec

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.entities import User
from app.users.exceptions import UserNotFoundError
from app.users.repository import UserRepository
from app.users.service import UserService

MOCK_AUTH0_ID = "auth0|123"


@pytest.fixture
def session() -> MagicMock:
    return create_autospec(AsyncSession, instance=True)


@pytest.fixture
def user_repository() -> MagicMock:
    return create_autospec(UserRepository, instance=True)


@pytest.fixture
def user_service(session: MagicMock, user_repository: MagicMock) -> UserService:
    return UserService(session, user_repository)


async def test_get_user_returns_correct_user(
    user_service: UserService, user_repository: MagicMock
) -> None:
    user = User()
    user.auth0_id = MOCK_AUTH0_ID

    user_repository.find_by_auth0_id.return_value = user

    result = await user_service.get_user(MOCK_AUTH0_ID)
    assert result == user


async def test_get_user_throws_user_not_found_exception_when_user_not_found(
    user_service: UserService, user_repository: MagicMock
) -> None:
    user_repository.find_by_auth0_id.return_value = None

    with pytest.raises(UserNotFoundError):
        await user_service.get_user(MOCK_AUTH0_ID)


async def test_ensure_user_saved_returns_true_when_upsert_affects_rows(
    user_service: UserService, user_repository: MagicMock
) -> None:
    user_repository.upsert_user.return_value = 1

    result = await user_service.ensure_user_saved(MOCK_AUTH0_ID)

    assert result is True


async def test_ensure_user_saved_returns_false_when_upsert_affects_no_rows(
    user_service: UserService, user_repository: MagicMock
) -> None:
    user_repository.upsert_user.return_value = 0

    result = await user_service.ensure_user_saved(MOCK_AUTH0_ID)

    assert result is False


async def test_ensure_user_saved_calls_repository_with_correct_id(
    user_service: UserService, user_repository: MagicMock
) -> None:
    user_repository.upsert_user.return_value = 1

    await user_service.ensure_user_saved("auth0|456")

    user_repository.upsert_user.assert_awaited_once_with("auth0|456")


# --- Beyond the JUnit suite: the @Transactional boundary ---


async def test_ensure_user_saved_commits_the_upsert(
    user_service: UserService, user_repository: MagicMock, session: MagicMock
) -> None:
    user_repository.upsert_user.return_value = 1

    await user_service.ensure_user_saved(MOCK_AUTH0_ID)

    session.commit.assert_awaited_once()
