"""Global exception handling. Mirrors exceptions/GlobalExceptionHandler.java.

Every error response has an empty body, as the Java ResponseEntity<Void> handlers did.
"""

import logging
from collections.abc import Mapping

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.auth.dependencies import authenticate_request, public_paths
from app.config import get_settings
from app.userbooks.exceptions import UnauthorizedUserBookAccessError, UserBookNotFoundError
from app.users.exceptions import UserNotFoundError

logger = logging.getLogger(__name__)

_ROUTING_STATUSES = frozenset({status.HTTP_404_NOT_FOUND, status.HTTP_405_METHOD_NOT_ALLOWED})
_SPRING_METHOD_ORDER = ("GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "TRACE")


def _empty(status_code: int, headers: Mapping[str, str] | None = None) -> Response:
    return Response(status_code=status_code, headers=dict(headers) if headers else None)


def _spring_allow_header(route_methods: set[str]) -> str:
    methods = set(route_methods) | {"OPTIONS"}
    if "GET" in methods:
        methods.add("HEAD")
    return ",".join(m for m in _SPRING_METHOD_ORDER if m in methods)


async def _authentication_failure(request: Request) -> Response | None:
    """Spring Security authenticated every secured request before MVC saw it.

    Errors raised before FastAPI runs the route's auth dependency (unmatched routes, unparseable
    JSON) must therefore still answer 401 to unauthenticated callers.
    """
    path = request.scope["path"]
    if not path.startswith(get_settings().api_prefix) or path in public_paths():
        return None
    try:
        await authenticate_request(request)
    except HTTPException as auth_error:
        return _empty(auth_error.status_code, auth_error.headers)
    return None


async def handle_user_not_found(request: Request, exc: Exception) -> Response:
    return _empty(status.HTTP_404_NOT_FOUND)


async def handle_user_book_not_found(request: Request, exc: Exception) -> Response:
    return _empty(status.HTTP_404_NOT_FOUND)


async def handle_unauthorized_access(request: Request, exc: Exception) -> Response:
    return _empty(status.HTTP_403_FORBIDDEN)


async def handle_request_validation(request: Request, exc: Exception) -> Response:
    if (auth_failure := await _authentication_failure(request)) is not None:
        return auth_failure
    # Spring's catch-all handler turned unreadable bodies and mistyped path variables into 500s.
    # Preserved deliberately for contract compatibility; 422 would be the idiomatic status.
    logger.info("Rejected invalid request input for %s %s", request.method, request.url.path)
    return _empty(status.HTTP_500_INTERNAL_SERVER_ERROR)


async def handle_http_exception(request: Request, exc: Exception) -> Response:
    assert isinstance(exc, StarletteHTTPException)
    if exc.status_code not in _ROUTING_STATUSES:
        return _empty(exc.status_code, exc.headers)

    if (auth_failure := await _authentication_failure(request)) is not None:
        return auth_failure

    if exc.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
        if request.method == "OPTIONS":
            # Spring MVC answers a plain OPTIONS on any mapped path with the supported methods.
            allow = (exc.headers or {}).get("Allow", "")
            route_methods = {method.strip() for method in allow.split(",") if method.strip()}
            return _empty(
                status.HTTP_200_OK,
                {"Allow": _spring_allow_header(route_methods), "Accept-Patch": ""},
            )
        # HttpRequestMethodNotSupportedException fell through to the catch-all handler.
        return _empty(status.HTTP_500_INTERNAL_SERVER_ERROR)
    return _empty(status.HTTP_404_NOT_FOUND)  # NoResourceFoundException


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(UserNotFoundError, handle_user_not_found)
    app.add_exception_handler(UserBookNotFoundError, handle_user_book_not_found)
    app.add_exception_handler(UnauthorizedUserBookAccessError, handle_unauthorized_access)
    app.add_exception_handler(RequestValidationError, handle_request_validation)
    app.add_exception_handler(StarletteHTTPException, handle_http_exception)
