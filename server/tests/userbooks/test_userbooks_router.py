"""Ports UserBooksControllerTest."""

from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, create_autospec

import pytest
from httpx import AsyncClient

from app.userbooks.enums import ReadingStatus
from app.userbooks.exceptions import UnauthorizedUserBookAccessError, UserBookNotFoundError
from app.userbooks.schemas import AddBookRequest, UserBookDTO
from app.userbooks.service import UserBooksService, get_user_books_service
from app.users.exceptions import UserNotFoundError

AUTH0_ID = "auth0|123"


@pytest.fixture
def user_books_service(override: Callable[[Callable[..., Any], Any], None]) -> MagicMock:
    service = create_autospec(UserBooksService, instance=True)
    override(get_user_books_service, service)
    return service


def _add_book_request_json() -> dict[str, Any]:
    request = AddBookRequest(
        title="Clean Code",
        author="Robert Martin",
        description="A coding book",
        reading_status=ReadingStatus.IN_PROGRESS,
    )
    # Serialized the way Jackson's ObjectMapper wrote the Java record.
    return request.model_dump(mode="json", by_alias=True)


# --- GET /userbooks/ ---


async def test_get_user_books_returns_200_with_book_list(
    auth_client: AsyncClient, user_books_service: MagicMock
) -> None:
    dto = UserBookDTO(
        id=1,
        title="Clean Code",
        author="Robert Martin",
        description="A coding book",
        reading_status="Reading",
    )
    user_books_service.get_all_user_books.return_value = [dto]

    response = await auth_client.get("/userbooks/")

    assert response.status_code == 200
    body = response.json()
    assert body[0]["title"] == "Clean Code"
    assert body[0]["author"] == "Robert Martin"
    # Response shape: the fields of the Java UserBookDTO record, in camelCase.
    assert body[0] == {
        "id": 1,
        "title": "Clean Code",
        "author": "Robert Martin",
        "description": "A coding book",
        "readingStatus": "Reading",
    }
    user_books_service.get_all_user_books.assert_awaited_once_with(AUTH0_ID)


async def test_get_user_books_returns_200_with_empty_list(
    auth_client: AsyncClient, user_books_service: MagicMock
) -> None:
    user_books_service.get_all_user_books.return_value = []

    response = await auth_client.get("/userbooks/")

    assert response.status_code == 200
    assert response.json() == []


# --- POST /userbooks/add-book ---


async def test_add_book_to_user_library_returns_200_with_updated_list(
    auth_client: AsyncClient, user_books_service: MagicMock
) -> None:
    dto = UserBookDTO(
        id=1,
        title="Clean Code",
        author="Robert Martin",
        description="A coding book",
        reading_status="Reading",
    )
    user_books_service.add_book_to_user_library.return_value = [dto]

    response = await auth_client.post("/userbooks/add-book", json=_add_book_request_json())

    assert response.status_code == 200
    assert response.json()[0]["title"] == "Clean Code"
    # any(AddBookRequest.class), eq(AUTH0_ID)
    request_arg, auth0_id_arg = user_books_service.add_book_to_user_library.await_args.args
    assert isinstance(request_arg, AddBookRequest)
    assert auth0_id_arg == AUTH0_ID


async def test_add_book_to_user_library_returns_404_when_user_not_found(
    auth_client: AsyncClient, user_books_service: MagicMock
) -> None:
    user_books_service.add_book_to_user_library.side_effect = UserNotFoundError(AUTH0_ID)

    response = await auth_client.post("/userbooks/add-book", json=_add_book_request_json())

    assert response.status_code == 404
    assert response.content == b""


# --- DELETE /userbooks/delete-book/{userBookId} ---


async def test_delete_book_from_user_library_returns_204_when_successful(
    auth_client: AsyncClient, user_books_service: MagicMock
) -> None:
    user_books_service.delete_book_from_user_library.return_value = None

    response = await auth_client.delete("/userbooks/delete-book/1")

    assert response.status_code == 204
    assert response.content == b""
    user_books_service.delete_book_from_user_library.assert_awaited_once_with(1, AUTH0_ID)


async def test_delete_book_from_user_library_returns_404_when_book_not_found(
    auth_client: AsyncClient, user_books_service: MagicMock
) -> None:
    user_books_service.delete_book_from_user_library.side_effect = UserBookNotFoundError(99)

    response = await auth_client.delete("/userbooks/delete-book/99")

    assert response.status_code == 404
    assert response.content == b""


async def test_delete_book_from_user_library_returns_403_when_user_does_not_own_book(
    auth_client: AsyncClient, user_books_service: MagicMock
) -> None:
    user_books_service.delete_book_from_user_library.side_effect = UnauthorizedUserBookAccessError(
        1, "auth0|owner", AUTH0_ID
    )

    response = await auth_client.delete("/userbooks/delete-book/1")

    assert response.status_code == 403
    assert response.content == b""
