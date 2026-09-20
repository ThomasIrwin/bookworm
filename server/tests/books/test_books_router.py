"""Ports BookControllerTest."""

from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, create_autospec

import pytest
from httpx import AsyncClient

from app.books.entities import Book
from app.books.service import BookService, get_book_service


@pytest.fixture
def library_service(override: Callable[[Callable[..., Any], Any], None]) -> MagicMock:
    service = create_autospec(BookService, instance=True)
    override(get_book_service, service)
    return service


@pytest.fixture
def test_books() -> tuple[Book, Book]:
    test_book1 = Book(
        title="Brave New World",
        author="Aldous Huxley",
        description="Prophetic dystopian novel from 1932 about future society",
    )
    test_book1.id = 1

    test_book2 = Book(
        title="Masters of the Air",
        author="Donald Miller",
        description="Gripping telling of the WWII bomber pilots who braved the skies over Germany",
    )
    test_book2.id = 2
    return test_book1, test_book2


async def test_get_user_library(
    auth_client: AsyncClient, library_service: MagicMock, test_books: tuple[Book, Book]
) -> None:
    library_service.get_all_books.return_value = list(test_books)

    response = await auth_client.get("/books/")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 2
    assert body[0]["title"] == "Brave New World"
    assert body[0]["author"] == "Aldous Huxley"
    assert body[1]["title"] == "Masters of the Air"
    assert body[1]["author"] == "Donald Miller"
    # Response shape: exactly the serialized fields of the Java Book entity.
    assert set(body[0]) == {"id", "title", "author", "description"}


async def test_when_health_endpoint_called_returns_expected_string(
    auth_client: AsyncClient, library_service: MagicMock
) -> None:
    library_service.check_application_health.return_value = "Application is healthy"

    response = await auth_client.get("/books/health")

    assert response.status_code == 200
    assert response.text == "Application is healthy"


async def test_when_non_existant_endpoint_called_returns_not_found(
    auth_client: AsyncClient,
) -> None:
    response = await auth_client.get("/nonexistent")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
