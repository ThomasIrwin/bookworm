"""Ports UserControllerTest."""

from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, create_autospec

import pytest
from httpx import AsyncClient

from app.users.service import UserService, get_user_service


@pytest.fixture
def user_service(override: Callable[[Callable[..., Any], Any], None]) -> MagicMock:
    service = create_autospec(UserService, instance=True)
    override(get_user_service, service)
    return service


async def test_when_unsaved_user_received_controller_returns_201_status_code(
    auth_client: AsyncClient, user_service: MagicMock
) -> None:
    user_service.ensure_user_saved.return_value = True

    response = await auth_client.post("/users/me")

    assert response.status_code == 201
    assert response.content == b""
    user_service.ensure_user_saved.assert_awaited_once_with("auth0|123")


async def test_when_saved_user_received_controller_returns_200_status_code(
    auth_client: AsyncClient, user_service: MagicMock
) -> None:
    user_service.ensure_user_saved.return_value = False

    response = await auth_client.post("/users/me")

    assert response.status_code == 200
    assert response.content == b""
    user_service.ensure_user_saved.assert_awaited_once_with("auth0|123")
