from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.auth.dependencies import CurrentAuth0Id
from app.userbooks.schemas import AddBookRequest, UserBookDTO
from app.userbooks.service import UserBooksService, get_user_books_service

router = APIRouter(prefix="/userbooks", tags=["userbooks"])

UserBooksServiceDep = Annotated[UserBooksService, Depends(get_user_books_service)]


@router.get("/", response_model=list[UserBookDTO])
async def get_user_books(
    auth0_id: CurrentAuth0Id, user_books_service: UserBooksServiceDep
) -> list[UserBookDTO]:
    return await user_books_service.get_all_user_books(auth0_id)


@router.post("/add-book", response_model=list[UserBookDTO])
async def add_book_to_user_library(
    auth0_id: CurrentAuth0Id, book: AddBookRequest, user_books_service: UserBooksServiceDep
) -> list[UserBookDTO]:
    return await user_books_service.add_book_to_user_library(book, auth0_id)


@router.delete(
    "/delete-book/{user_book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_book_from_user_library(
    auth0_id: CurrentAuth0Id, user_book_id: int, user_books_service: UserBooksServiceDep
) -> Response:
    await user_books_service.delete_book_from_user_library(user_book_id, auth0_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
