"""Mirrors userbooks/UserBooksController.java."""

import re
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Request, Response, status
from fastapi.exceptions import RequestValidationError
from pydantic import BeforeValidator

from app.auth.dependencies import CurrentAuth0Id
from app.userbooks.schemas import AddBookRequest, UserBookDTO
from app.userbooks.service import UserBooksService, get_user_books_service

router = APIRouter(prefix="/userbooks", tags=["userbooks"])

UserBooksServiceDep = Annotated[UserBooksService, Depends(get_user_books_service)]

_DECIMAL_LONG = re.compile(r"[+-]?[0-9]+")


def _parse_long_path_variable(value: object) -> object:
    """Bind like Spring: surrounding whitespace is trimmed, then only a signed decimal is accepted.

    Pydantic alone would also accept "1.0" and "1_000", which Spring rejected.
    """
    if not isinstance(value, str):
        return value
    trimmed = value.strip()
    if not _DECIMAL_LONG.fullmatch(trimmed):
        raise ValueError("path variable is not a valid long")
    return int(trimmed)


# A Java Long path variable: out-of-range ids fail binding instead of reaching the database.
UserBookId = Annotated[
    int, BeforeValidator(_parse_long_path_variable), Path(ge=-(2**63), le=2**63 - 1)
]


def require_json_content_type(request: Request) -> None:
    """Spring rejected bodies without a JSON media type; FastAPI would parse them as JSON anyway."""
    media_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if media_type == "application/json" or (
        media_type.startswith("application/") and media_type.endswith("+json")
    ):
        return
    raise RequestValidationError(
        [
            {
                "type": "unsupported_media_type",
                "loc": ("header", "content-type"),
                "msg": "Content type must be JSON",
                "input": media_type,
            }
        ]
    )


@router.get("/", response_model=list[UserBookDTO])
async def get_user_books(
    auth0_id: CurrentAuth0Id, user_books_service: UserBooksServiceDep
) -> list[UserBookDTO]:
    return await user_books_service.get_all_user_books(auth0_id)


@router.post("/add-book", response_model=list[UserBookDTO])
async def add_book_to_user_library(
    auth0_id: CurrentAuth0Id,
    _json_body: Annotated[None, Depends(require_json_content_type)],
    book: AddBookRequest,
    user_books_service: UserBooksServiceDep,
) -> list[UserBookDTO]:
    return await user_books_service.add_book_to_user_library(book, auth0_id)


@router.delete(
    "/delete-book/{user_book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_book_from_user_library(
    auth0_id: CurrentAuth0Id, user_book_id: UserBookId, user_books_service: UserBooksServiceDep
) -> Response:
    await user_books_service.delete_book_from_user_library(user_book_id, auth0_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
