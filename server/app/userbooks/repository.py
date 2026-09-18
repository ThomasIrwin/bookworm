from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.userbooks.entities import UserBook
from app.users.entities import User


class UserBookRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, user_book: UserBook) -> UserBook:
        self._session.add(user_book)
        await self._session.flush()
        return user_book

    async def find_all_by_user_auth0_id(self, user_auth0_id: str) -> list[UserBook]:
        """All of a user's books, with each book eagerly loaded."""
        result = await self._session.scalars(
            select(UserBook)
            .join(UserBook.user)
            .where(User.auth0_id == user_auth0_id)
            .options(selectinload(UserBook.book))
            .order_by(UserBook.id)
        )
        return list(result)

    async def find_by_id(self, user_book_id: int) -> UserBook | None:
        """A user book with its owning user eagerly loaded, for ownership checks."""
        result = await self._session.scalars(
            select(UserBook).where(UserBook.id == user_book_id).options(selectinload(UserBook.user))
        )
        return result.one_or_none()

    async def delete_by_id(self, user_book_id: int) -> None:
        await self._session.execute(delete(UserBook).where(UserBook.id == user_book_id))
