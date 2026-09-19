from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.books.entities import Book
from app.books.service import BookService, get_book_service
from app.database import get_session
from app.userbooks.entities import UserBook
from app.userbooks.exceptions import UnauthorizedUserBookAccessError, UserBookNotFoundError
from app.userbooks.repository import UserBookRepository
from app.userbooks.schemas import AddBookRequest, UserBookDTO
from app.users.service import UserService, get_user_service


class UserBooksService:
    """Each public method is one transaction, as with the class-level @Transactional it replaces."""

    def __init__(
        self,
        session: AsyncSession,
        user_book_repository: UserBookRepository,
        user_service: UserService,
        book_service: BookService,
    ) -> None:
        self._session = session
        self._user_book_repository = user_book_repository
        self._user_service = user_service
        self._book_service = book_service

    async def get_all_user_books(self, user_auth0_id: str) -> list[UserBookDTO]:
        user_books = await self._user_book_repository.find_all_by_user_auth0_id(user_auth0_id)
        return [
            UserBookDTO(
                id=user_book.id,
                title=user_book.book.title,
                author=user_book.book.author,
                description=user_book.book.description,
                reading_status=user_book.reading_status.display_name,
            )
            for user_book in user_books
        ]

    async def add_book_to_user_library(
        self, book: AddBookRequest, user_auth0_id: str
    ) -> list[UserBookDTO]:
        current_user = await self._user_service.get_user(user_auth0_id)

        new_book = await self._book_service.get_book(book.title, book.author)
        if new_book is None:
            new_book = Book(title=book.title, author=book.author, description=book.description)
            await self._book_service.save_book(new_book)

        new_user_book = UserBook(
            user=current_user, book=new_book, reading_status=book.reading_status
        )
        await self._user_book_repository.save(new_user_book)
        await self._session.commit()

        return await self.get_all_user_books(user_auth0_id)

    async def delete_book_from_user_library(self, user_book_id: int, user_auth0_id: str) -> None:
        user_book = await self._user_book_repository.find_by_id(user_book_id)
        if user_book is None:
            raise UserBookNotFoundError(user_book_id)

        saved_user_book_auth0_id = user_book.user.auth0_id
        if saved_user_book_auth0_id != user_auth0_id:
            raise UnauthorizedUserBookAccessError(
                user_book_id, saved_user_book_auth0_id, user_auth0_id
            )

        await self._user_book_repository.delete_by_id(user_book_id)
        await self._session.commit()


def get_user_books_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    book_service: Annotated[BookService, Depends(get_book_service)],
) -> UserBooksService:
    return UserBooksService(session, UserBookRepository(session), user_service, book_service)
