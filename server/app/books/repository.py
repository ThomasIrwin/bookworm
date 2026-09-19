from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.books.entities import Book


def _escape_like(value: str) -> str:
    # Spring Data escapes wildcards in derived "Containing" queries; do the same.
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


class BookRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, book: Book) -> Book:
        self._session.add(book)
        await self._session.flush()
        return book

    async def find_all(self) -> list[Book]:
        result = await self._session.scalars(select(Book).order_by(Book.id))
        return list(result)

    async def find_by_title_containing_ignore_case(self, title: str) -> list[Book]:
        pattern = f"%{_escape_like(title)}%"
        result = await self._session.scalars(
            select(Book).where(Book.title.ilike(pattern, escape="\\")).order_by(Book.id)
        )
        return list(result)

    async def find_by_title_and_author(self, title: str | None, author: str | None) -> Book | None:
        # Comparing to None renders IS NULL, matching Spring Data's derived-query null handling.
        result = await self._session.scalars(
            select(Book).where(Book.title == title, Book.author == author)
        )
        return result.one_or_none()
