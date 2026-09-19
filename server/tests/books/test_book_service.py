"""Ports BookServiceTest."""

from unittest.mock import MagicMock, create_autospec

import pytest
from pydantic import ValidationError

from app.books.entities import Book
from app.books.exceptions import NullBookError
from app.books.repository import BookRepository
from app.books.service import BookService


@pytest.fixture
def book_repository() -> MagicMock:
    return create_autospec(BookRepository, instance=True)


@pytest.fixture
def book_service(book_repository: MagicMock) -> BookService:
    return BookService(book_repository)


@pytest.fixture
def test_book1() -> Book:
    book = Book(
        title="Brave New World",
        author="Aldous Huxley",
        description="Prophetic dystopian novel from 1932 about future society",
    )
    book.id = 1
    return book


@pytest.fixture
def test_book2() -> Book:
    book = Book(
        title="Masters of the Air",
        author="Donald Miller",
        description="Gripping telling of the WWII bomber pilots who braved the skies over Germany",
    )
    book.id = 2
    return book


async def test_save_book_book_saves_to_repository(
    book_service: BookService, book_repository: MagicMock, test_book1: Book
) -> None:
    await book_service.save_book(test_book1)

    book_repository.save.assert_awaited_once_with(test_book1)


async def test_get_all_books_returns_correct_books(
    book_service: BookService, book_repository: MagicMock, test_book1: Book, test_book2: Book
) -> None:
    expected_books = [test_book1, test_book2]
    book_repository.find_all.return_value = expected_books

    actual_books = await book_service.get_all_books()

    assert len(actual_books) == 2
    assert actual_books == [test_book1, test_book2]
    book_repository.find_all.assert_awaited_once()


def test_check_application_health_returns_correct_string(book_service: BookService) -> None:
    expected = "Application is healthy"
    actual = book_service.check_application_health()
    assert actual == expected


# --- Beyond the JUnit suite: behaviour BookService implements but never tested ---


async def test_save_book_raises_null_book_error_when_book_is_none(
    book_service: BookService, book_repository: MagicMock
) -> None:
    with pytest.raises(NullBookError, match="Attempted to save a book with a value of null"):
        await book_service.save_book(None)

    book_repository.save.assert_not_awaited()


async def test_save_book_rejects_invalid_book_before_persisting(
    book_service: BookService, book_repository: MagicMock
) -> None:
    with pytest.raises(ValidationError, match="Title is required"):
        await book_service.save_book(Book(title=" ", author="Valid Author"))

    book_repository.save.assert_not_awaited()
