"""Ports UserBooksServiceTest (UserBookServiceTest.java)."""

from unittest.mock import MagicMock, create_autospec

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.books.entities import Book
from app.books.service import BookService
from app.userbooks.entities import UserBook
from app.userbooks.enums import ReadingStatus
from app.userbooks.exceptions import UnauthorizedUserBookAccessError, UserBookNotFoundError
from app.userbooks.repository import UserBookRepository
from app.userbooks.schemas import AddBookRequest
from app.userbooks.service import UserBooksService
from app.users.entities import User
from app.users.service import UserService


@pytest.fixture
def session() -> MagicMock:
    return create_autospec(AsyncSession, instance=True)


@pytest.fixture
def user_book_repo() -> MagicMock:
    return create_autospec(UserBookRepository, instance=True)


@pytest.fixture
def user_service() -> MagicMock:
    return create_autospec(UserService, instance=True)


@pytest.fixture
def book_service() -> MagicMock:
    service = create_autospec(BookService, instance=True)
    # Mockito's default for an Optional return is Optional.empty().
    service.get_book.return_value = None
    return service


@pytest.fixture
def user_books_service(
    session: MagicMock, user_book_repo: MagicMock, user_service: MagicMock, book_service: MagicMock
) -> UserBooksService:
    return UserBooksService(session, user_book_repo, user_service, book_service)


async def test_get_all_user_books_returns_mapped_dtos(
    user_books_service: UserBooksService, user_book_repo: MagicMock
) -> None:
    user = User()
    user.auth0_id = "auth0|123"

    book = Book(
        title="Clean Code", author="Robert Martin", description="A book about writing clean code"
    )

    user_book = UserBook(user=user, book=book, reading_status=ReadingStatus.IN_PROGRESS)
    user_book.id = 1

    user_book_repo.find_all_by_user_auth0_id.return_value = [user_book]

    result = await user_books_service.get_all_user_books("auth0|123")

    assert len(result) == 1
    dto = result[0]
    assert dto.id == 1
    assert dto.title == "Clean Code"
    assert dto.author == "Robert Martin"
    assert dto.description == "A book about writing clean code"
    assert dto.reading_status == ReadingStatus.IN_PROGRESS.display_name


async def test_get_all_user_books_returns_empty_list_when_no_books_found(
    user_books_service: UserBooksService, user_book_repo: MagicMock
) -> None:
    user_book_repo.find_all_by_user_auth0_id.return_value = []

    result = await user_books_service.get_all_user_books("auth0|123")

    assert result == []


async def test_add_book_to_user_library_saves_book_and_user_book(
    user_books_service: UserBooksService,
    user_book_repo: MagicMock,
    user_service: MagicMock,
    book_service: MagicMock,
) -> None:
    user = User()
    user.auth0_id = "auth0|123"

    request = AddBookRequest(
        title="Clean Code",
        author="Robert Martin",
        description="A coding book",
        reading_status=ReadingStatus.IN_PROGRESS,
    )

    user_service.get_user.return_value = user
    user_book_repo.find_all_by_user_auth0_id.return_value = []

    await user_books_service.add_book_to_user_library(request, "auth0|123")

    book_service.save_book.assert_awaited_once()
    saved_book = book_service.save_book.await_args.args[0]
    assert saved_book.title == "Clean Code"

    user_book_repo.save.assert_awaited_once()
    saved_user_book = user_book_repo.save.await_args.args[0]
    assert saved_user_book.user == user
    assert saved_user_book.status == ReadingStatus.IN_PROGRESS


async def test_delete_book_from_user_library_throws_user_book_not_found_when_book_does_not_exist(
    user_books_service: UserBooksService, user_book_repo: MagicMock
) -> None:
    user_book_repo.find_by_id.return_value = None

    with pytest.raises(UserBookNotFoundError):
        await user_books_service.delete_book_from_user_library(99, "auth0|123")


async def test_delete_book_from_user_library_throws_unauthorized_when_user_does_not_own_book(
    user_books_service: UserBooksService, user_book_repo: MagicMock
) -> None:
    owner = User()
    owner.auth0_id = "auth0|owner"

    user_book = UserBook(user=owner, book=Book(), reading_status=ReadingStatus.IN_PROGRESS)
    user_book.id = 1

    user_book_repo.find_by_id.return_value = user_book

    with pytest.raises(UnauthorizedUserBookAccessError):
        await user_books_service.delete_book_from_user_library(1, "auth0|intruder")


async def test_delete_book_from_user_library_deletes_book_when_authorized(
    user_books_service: UserBooksService, user_book_repo: MagicMock
) -> None:
    user = User()
    user.auth0_id = "auth0|123"

    user_book = UserBook(user=user, book=Book(), reading_status=ReadingStatus.IN_PROGRESS)
    user_book.id = 1

    user_book_repo.find_by_id.return_value = user_book

    await user_books_service.delete_book_from_user_library(1, "auth0|123")

    user_book_repo.delete_by_id.assert_awaited_once_with(1)


# --- Beyond the JUnit suite: de-duplication and transaction boundaries ---


async def test_add_book_to_user_library_reuses_existing_book(
    user_books_service: UserBooksService,
    user_book_repo: MagicMock,
    user_service: MagicMock,
    book_service: MagicMock,
    session: MagicMock,
) -> None:
    user = User(auth0_id="auth0|123")
    existing_book = Book(title="Clean Code", author="Robert Martin")
    user_service.get_user.return_value = user
    book_service.get_book.return_value = existing_book
    user_book_repo.find_all_by_user_auth0_id.return_value = []

    request = AddBookRequest(
        title="Clean Code", author="Robert Martin", reading_status=ReadingStatus.FINISHED
    )
    await user_books_service.add_book_to_user_library(request, "auth0|123")

    book_service.save_book.assert_not_awaited()
    assert user_book_repo.save.await_args.args[0].book is existing_book
    session.commit.assert_awaited_once()


async def test_add_book_to_user_library_does_not_commit_when_user_not_found(
    user_books_service: UserBooksService,
    user_service: MagicMock,
    book_service: MagicMock,
    session: MagicMock,
) -> None:
    from app.users.exceptions import UserNotFoundError

    user_service.get_user.side_effect = UserNotFoundError("auth0|123")

    with pytest.raises(UserNotFoundError):
        await user_books_service.add_book_to_user_library(AddBookRequest(), "auth0|123")

    book_service.save_book.assert_not_awaited()
    session.commit.assert_not_awaited()


async def test_delete_book_from_user_library_commits_only_when_authorized(
    user_books_service: UserBooksService, user_book_repo: MagicMock, session: MagicMock
) -> None:
    user_book = UserBook(
        user=User(auth0_id="auth0|owner"), book=Book(), reading_status=ReadingStatus.FINISHED
    )
    user_book_repo.find_by_id.return_value = user_book

    with pytest.raises(UnauthorizedUserBookAccessError):
        await user_books_service.delete_book_from_user_library(1, "auth0|intruder")
    session.commit.assert_not_awaited()

    await user_books_service.delete_book_from_user_library(1, "auth0|owner")
    session.commit.assert_awaited_once()
