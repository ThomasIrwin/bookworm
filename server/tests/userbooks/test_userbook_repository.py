"""UserBookRepository against PostgreSQL. The Java suite had no equivalent.

These tests are the guard for async loading: every relationship a service reads must be eagerly
loaded by the query, or access raises instead of silently querying as Hibernate did.
"""

import pytest
from sqlalchemy import text
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncSession

from app.books.entities import Book
from app.userbooks.entities import UserBook
from app.userbooks.enums import ReadingStatus
from app.userbooks.repository import UserBookRepository
from app.users.entities import User

pytestmark = pytest.mark.integration


@pytest.fixture
def repository(session: AsyncSession) -> UserBookRepository:
    return UserBookRepository(session)


@pytest.fixture
async def library(session: AsyncSession) -> dict[str, int]:
    alice = User(auth0_id="auth0|alice")
    bob = User(auth0_id="auth0|bob")
    dune = Book(title="Dune", author="Frank Herbert")
    emma = Book(title="Emma", author="Jane Austen", description="A comedy of manners")
    alice_dune = UserBook(user=alice, book=dune, reading_status=ReadingStatus.IN_PROGRESS)
    alice_emma = UserBook(user=alice, book=emma, reading_status=ReadingStatus.FINISHED)
    bob_dune = UserBook(user=bob, book=dune, reading_status=ReadingStatus.WANT_TO_READ)

    session.add_all([alice_dune, alice_emma, bob_dune])
    await session.flush()
    ids = {"alice_dune": alice_dune.id, "alice_emma": alice_emma.id, "bob_dune": bob_dune.id}
    session.expunge_all()  # later reads must come from the database, not the identity map
    return ids


async def test_find_all_by_user_auth0_id_returns_only_that_users_books_with_books_loaded(
    repository: UserBookRepository, library: dict[str, int]
) -> None:
    user_books = await repository.find_all_by_user_auth0_id("auth0|alice")

    assert [ub.id for ub in user_books] == [library["alice_dune"], library["alice_emma"]]
    assert [(ub.book.title, ub.book.description) for ub in user_books] == [
        ("Dune", None),
        ("Emma", "A comedy of manners"),
    ]
    assert [ub.reading_status for ub in user_books] == [
        ReadingStatus.IN_PROGRESS,
        ReadingStatus.FINISHED,
    ]


@pytest.mark.usefixtures("library")
async def test_relationships_not_eagerly_loaded_raise_instead_of_lazy_loading(
    repository: UserBookRepository,
) -> None:
    user_books = await repository.find_all_by_user_auth0_id("auth0|alice")

    with pytest.raises(InvalidRequestError):
        _ = user_books[0].user


@pytest.mark.usefixtures("library")
async def test_find_all_by_user_auth0_id_returns_empty_for_unknown_user(
    repository: UserBookRepository,
) -> None:
    assert await repository.find_all_by_user_auth0_id("auth0|nobody") == []


async def test_find_by_id_loads_the_owning_user(
    repository: UserBookRepository, library: dict[str, int]
) -> None:
    user_book = await repository.find_by_id(library["bob_dune"])

    assert user_book is not None
    assert user_book.user.auth0_id == "auth0|bob"


@pytest.mark.usefixtures("library")
async def test_find_by_id_returns_none_when_missing(repository: UserBookRepository) -> None:
    assert await repository.find_by_id(987654321) is None


async def test_delete_by_id_removes_only_that_row(
    session: AsyncSession, repository: UserBookRepository, library: dict[str, int]
) -> None:
    await repository.delete_by_id(library["alice_dune"])
    await repository.delete_by_id(987654321)  # absent ids are ignored, as in Spring Data 3

    assert await repository.find_by_id(library["alice_dune"]) is None
    assert await repository.find_by_id(library["bob_dune"]) is not None


async def test_reading_status_is_stored_by_name(
    session: AsyncSession, library: dict[str, int]
) -> None:
    stored = await session.scalar(
        text("SELECT reading_status FROM user_books WHERE id = :id"),
        {"id": library["bob_dune"]},
    )

    assert stored == "WANT_TO_READ"
