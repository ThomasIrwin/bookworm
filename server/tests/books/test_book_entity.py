"""Ports BookTest.

Jakarta Bean Validation on the Java entity becomes the BookCreate model, which BookService applies
to a Book before persisting it.
"""

from pydantic import ValidationError
from pydantic_core import ErrorDetails

from app.books.entities import Book
from app.books.schemas import BookCreate


def validate(book: Book) -> list[ErrorDetails]:
    try:
        BookCreate.model_validate(book)
    except ValidationError as violations:
        return violations.errors()
    return []


def test_valid_book() -> None:
    book = Book(title="Valid Title", author="Valid Author", description="Valid description")

    violations = validate(book)

    assert violations == []


def test_blank_title() -> None:
    book = Book(title="", author="Valid Author", description="Valid description")

    violations = validate(book)

    assert len(violations) == 1
    assert violations[0]["msg"] == "Title is required"


def test_blank_author() -> None:
    book = Book(title="Valid Title", author="", description="Valid description")

    violations = validate(book)

    assert len(violations) == 1
    assert violations[0]["msg"] == "Author is required"


def test_null_description() -> None:
    book = Book(title="Valid Title", author="Valid Author", description=None)

    violations = validate(book)

    assert violations == []  # Description is optional


def test_book_constructor_and_getters() -> None:
    book = Book(title="Test Title", author="Test Author", description="Test Description")
    book.id = 1

    assert book.title == "Test Title"
    assert book.author == "Test Author"
    assert book.description == "Test Description"
    assert book.id == 1
