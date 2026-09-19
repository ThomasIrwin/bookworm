"""Mirrors books/BooksController.java."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from app.auth.dependencies import authenticate_if_bearer_present, get_current_auth0_id
from app.books.entities import Book
from app.books.schemas import BookOut
from app.books.service import BookService, get_book_service

router = APIRouter(prefix="/books", tags=["books"])

BookServiceDep = Annotated[BookService, Depends(get_book_service)]


class SpringPlainTextResponse(PlainTextResponse):
    media_type = "text/plain;charset=UTF-8"


@router.get("/", response_model=list[BookOut], dependencies=[Depends(get_current_auth0_id)])
async def get_all_books(library_service: BookServiceDep) -> list[Book]:
    return await library_service.get_all_books()


@router.get(
    "/health",
    response_class=SpringPlainTextResponse,
    dependencies=[Depends(authenticate_if_bearer_present)],
)
async def health(library_service: BookServiceDep) -> str:
    return library_service.check_application_health()
