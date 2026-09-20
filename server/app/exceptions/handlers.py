"""Global exception handling: maps domain errors to HTTP responses.

A genuine unhandled exception is handled by CatchAllExceptionMiddleware instead of a handler
registered here: see its docstring for why that has to be middleware, not an exception handler.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.userbooks.exceptions import UnauthorizedUserBookAccessError, UserBookNotFoundError
from app.users.exceptions import UserNotFoundError


async def handle_user_not_found(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse({"detail": "User not found"}, status_code=404)


async def handle_user_book_not_found(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse({"detail": "User book not found"}, status_code=404)


async def handle_unauthorized_access(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse({"detail": "Forbidden"}, status_code=403)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(UserNotFoundError, handle_user_not_found)
    app.add_exception_handler(UserBookNotFoundError, handle_user_book_not_found)
    app.add_exception_handler(UnauthorizedUserBookAccessError, handle_unauthorized_access)
