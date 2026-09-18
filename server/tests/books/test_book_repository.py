"""Ports BookRepositoryTest (@DataJpaTest with a Testcontainers PostgreSQL)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.books.entities import Book
from app.books.repository import BookRepository

pytestmark = pytest.mark.integration


@pytest.fixture
def test_book_repository(session: AsyncSession) -> BookRepository:
    return BookRepository(session)


@pytest.fixture
async def test_books(session: AsyncSession) -> tuple[Book, Book, Book]:
    test_book1 = Book(
        title="Brave New World",
        author="Aldous Huxley",
        description="Prophetic dystopian novel from 1932 about future society",
    )
    test_book2 = Book(
        title="Masters of the Air",
        author="Donald Miller",
        description="Gripping telling of the WWII bomber pilots who braved the skies over Germany",
    )
    test_book3 = Book(
        title="The Rise of Theodore Roosevelt",
        author="Edmund Morris",
        description=(
            "Depicts the early life of one of the most influential presidents in U.S. History"
        ),
    )

    session.add_all([test_book1, test_book2, test_book3])
    await session.flush()
    return test_book1, test_book2, test_book3


@pytest.mark.usefixtures("test_books")
async def test_find_by_title_containing_ignore_case(test_book_repository: BookRepository) -> None:
    books = await test_book_repository.find_by_title_containing_ignore_case("of")

    assert len(books) == 2
    assert sorted(book.title for book in books) == sorted(
        ["Masters of the Air", "The Rise of Theodore Roosevelt"]
    )


@pytest.mark.usefixtures("test_books")
async def test_find_by_title_containing_ignore_case_case_insensitive(
    test_book_repository: BookRepository,
) -> None:
    books = await test_book_repository.find_by_title_containing_ignore_case("MASTERS")

    assert len(books) == 1
    assert books[0].title == "Masters of the Air"


async def test_find_by_title_and_author_book_exists(
    session: AsyncSession,
    test_book_repository: BookRepository,
    test_books: tuple[Book, Book, Book],
) -> None:
    session.expunge_all()

    book = await test_book_repository.find_by_title_and_author(
        "Masters of the Air", "Donald Miller"
    )
    assert book is not None
    assert book == test_books[1]
    assert book is not test_books[1]  # a fresh instance loaded from the database


@pytest.mark.usefixtures("test_books")
async def test_find_by_title_and_author_book_not_found(
    test_book_repository: BookRepository,
) -> None:
    book = await test_book_repository.find_by_title_and_author("Doesn't exist", "John Doe")
    assert book is None


# --- Beyond the JUnit suite ---


@pytest.mark.usefixtures("test_books")
@pytest.mark.parametrize("wildcard", ["%", "_"])
async def test_find_by_title_containing_treats_like_wildcards_literally(
    test_book_repository: BookRepository, wildcard: str
) -> None:
    assert await test_book_repository.find_by_title_containing_ignore_case(wildcard) == []
