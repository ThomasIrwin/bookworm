"""Ports UserBookTest."""

from app.books.entities import Book
from app.userbooks.entities import UserBook
from app.userbooks.enums import ReadingStatus
from app.users.entities import User


def test_no_arg_constructor_creates_instance_with_null_fields() -> None:
    user_book = UserBook()

    assert user_book.id is None
    assert user_book.user is None
    assert user_book.book is None
    assert user_book.status is None


def test_parameterised_constructor_sets_fields_correctly() -> None:
    user = User()
    book = Book()

    user_book = UserBook(user=user, book=book, status=ReadingStatus.IN_PROGRESS)

    assert user_book.user == user
    assert user_book.book == book
    assert user_book.status == ReadingStatus.IN_PROGRESS


def test_set_id_and_get_id_work_correctly() -> None:
    user_book = UserBook()
    user_book.id = 42

    assert user_book.id == 42


def test_set_user_and_get_user_work_correctly() -> None:
    user = User()
    user_book = UserBook()
    user_book.user = user

    assert user_book.user == user


def test_set_book_and_get_book_work_correctly() -> None:
    book = Book()
    user_book = UserBook()
    user_book.book = book

    assert user_book.book == book


def test_set_status_and_get_status_work_correctly() -> None:
    user_book = UserBook()
    user_book.status = ReadingStatus.FINISHED

    assert user_book.status == ReadingStatus.FINISHED
    assert user_book.reading_status == ReadingStatus.FINISHED
