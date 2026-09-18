from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.books.entities import Book
from app.books.exceptions import NullBookError
from app.books.repository import BookRepository
from app.books.schemas import BookCreate
from app.database import get_session


class BookService:
    def __init__(self, book_repository: BookRepository) -> None:
        self._book_repository = book_repository

    # TODO: Remove once ETL pipelines are in place.
    # Book creation is temporarily user-facing until the database is populated.
    async def save_book(self, book: Book | None) -> None:
        """Stage a book in the current transaction. The calling service commits."""
        if book is None:
            raise NullBookError()
        # Hibernate Validator enforced the entity's constraints on persist; keep that guarantee.
        BookCreate.model_validate(book)
        await self._book_repository.save(book)

    async def get_book(self, title: str | None, author: str | None) -> Book | None:
        return await self._book_repository.find_by_title_and_author(title, author)

    async def get_all_books(self) -> list[Book]:
        return await self._book_repository.find_all()

    def check_application_health(self) -> str:
        return "Application is healthy"


def get_book_service(session: Annotated[AsyncSession, Depends(get_session)]) -> BookService:
    return BookService(BookRepository(session))
