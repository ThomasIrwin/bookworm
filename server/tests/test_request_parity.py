"""Request binding parity with Spring MVC and Jackson.

Every expectation here was recorded from the Spring Boot service before migration. Spring's
catch-all exception handler answered unbindable input with an empty 500, which is preserved.
"""

from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, create_autospec

import pytest
from httpx import AsyncClient

from app.userbooks.enums import ReadingStatus
from app.userbooks.schemas import AddBookRequest
from app.userbooks.service import UserBooksService, get_user_books_service

JSON = {"Content-Type": "application/json"}


@pytest.fixture
def user_books_service(override: Callable[[Callable[..., Any], Any], None]) -> MagicMock:
    service = create_autospec(UserBooksService, instance=True)
    service.add_book_to_user_library.return_value = []
    service.delete_book_from_user_library.return_value = None
    override(get_user_books_service, service)
    return service


def received_request(service: MagicMock) -> AddBookRequest:
    request: AddBookRequest = service.add_book_to_user_library.await_args.args[0]
    return request


# --- Request bodies Spring rejected ----------------------------------------------------------


@pytest.mark.parametrize(
    ("content", "headers"),
    [
        (b"{not json", JSON),
        (b"", JSON),
        (b"null", JSON),
        (b"[]", JSON),
        (b"x", {"Content-Type": "text/plain"}),
        (b'{"title":"T"}', {}),
        (b'{"title":"T","author":"A","readingStatus":"NOPE"}', JSON),
        (b'{"title":"T","author":"A","readingStatus":"in_progress"}', JSON),
        (b'{"title":"T","author":"A","readingStatus":"In Progress"}', JSON),
        (b'{"title":"T","author":"A","readingStatus":""}', JSON),
        (b'{"title":"T","author":"A","readingStatus":9}', JSON),
        (b'{"title":{},"author":"A","readingStatus":"IN_PROGRESS"}', JSON),
    ],
    ids=[
        "malformed-json",
        "empty-body",
        "json-null",
        "json-array",
        "text-plain",
        "no-content-type",
        "unknown-enum",
        "lowercase-enum",
        "display-name-enum",
        "empty-enum",
        "out-of-range-ordinal",
        "object-title",
    ],
)
async def test_unbindable_add_book_request_is_an_empty_500(
    auth_client: AsyncClient,
    user_books_service: MagicMock,
    content: bytes,
    headers: dict[str, str],
) -> None:
    response = await auth_client.post("/userbooks/add-book", content=content, headers=headers)

    assert response.status_code == 500
    assert response.content == b""
    user_books_service.add_book_to_user_library.assert_not_awaited()


async def test_malformed_body_without_token_is_401_not_500(client: AsyncClient) -> None:
    response = await client.post("/userbooks/add-book", content=b"{not json", headers=JSON)

    assert response.status_code == 401


# --- Request bodies Jackson accepted ---------------------------------------------------------


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        (
            {"title": "T", "author": "A", "readingStatus": "IN_PROGRESS", "extra": 1},
            AddBookRequest(title="T", author="A", reading_status=ReadingStatus.IN_PROGRESS),
        ),
        ({}, AddBookRequest()),
        (
            {"title": 123, "author": True, "description": 1.5, "readingStatus": "FINISHED"},
            AddBookRequest(
                title="123",
                author="true",
                description="1.5",
                reading_status=ReadingStatus.FINISHED,
            ),
        ),
        (
            {"title": "T", "author": "A", "readingStatus": 1},
            AddBookRequest(title="T", author="A", reading_status=ReadingStatus.IN_PROGRESS),
        ),
        (
            {"title": "T", "author": "A", "readingStatus": "3"},
            AddBookRequest(title="T", author="A", reading_status=ReadingStatus.PUT_DOWN),
        ),
    ],
    ids=[
        "unknown-field-ignored",
        "empty-object",
        "scalars-coerced",
        "enum-ordinal",
        "ordinal-string",
    ],
)
async def test_lenient_add_book_request_is_bound_like_jackson(
    auth_client: AsyncClient,
    user_books_service: MagicMock,
    body: dict[str, Any],
    expected: AddBookRequest,
) -> None:
    response = await auth_client.post("/userbooks/add-book", json=body)

    assert response.status_code == 200
    assert received_request(user_books_service) == expected


async def test_json_suffix_media_type_is_accepted(
    auth_client: AsyncClient, user_books_service: MagicMock
) -> None:
    response = await auth_client.post(
        "/userbooks/add-book",
        content=b'{"title":"T"}',
        headers={"Content-Type": "application/vnd.bookworm+json; charset=utf-8"},
    )

    assert response.status_code == 200


# --- Path variables --------------------------------------------------------------------------


@pytest.mark.parametrize("raw_id", ["abc", "1.0", "1_000", "1e3", "99999999999999999999"])
async def test_unbindable_user_book_id_is_an_empty_500(
    auth_client: AsyncClient, user_books_service: MagicMock, raw_id: str
) -> None:
    response = await auth_client.delete(f"/userbooks/delete-book/{raw_id}")

    assert response.status_code == 500
    assert response.content == b""
    user_books_service.delete_book_from_user_library.assert_not_awaited()


@pytest.mark.parametrize(
    ("raw_id", "user_book_id"),
    [("1", 1), ("+1", 1), ("%201", 1), ("-1", -1), ("9223372036854775807", 2**63 - 1)],
)
async def test_long_user_book_id_is_bound_like_spring(
    auth_client: AsyncClient, user_books_service: MagicMock, raw_id: str, user_book_id: int
) -> None:
    response = await auth_client.delete(f"/userbooks/delete-book/{raw_id}")

    assert response.status_code == 204
    user_books_service.delete_book_from_user_library.assert_awaited_once_with(
        user_book_id, "auth0|123"
    )


async def test_missing_user_book_id_is_not_found(auth_client: AsyncClient) -> None:
    response = await auth_client.delete("/userbooks/delete-book/")

    assert response.status_code == 404
