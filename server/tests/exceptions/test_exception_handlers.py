"""Ports GlobalExceptionHandlerTest, including its throwaway TestController."""

from collections.abc import AsyncIterator

import pytest
from fastapi import APIRouter, FastAPI
from httpx import ASGITransport, AsyncClient
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions.handlers import register_exception_handlers
from app.middleware import CatchAllExceptionMiddleware
from app.userbooks.exceptions import UnauthorizedUserBookAccessError, UserBookNotFoundError
from app.users.exceptions import UserNotFoundError


def _make_test_app() -> FastAPI:
    test_controller = APIRouter(prefix="/test")

    @test_controller.get("/user-not-found")
    async def throw_user_not_found() -> None:
        raise UserNotFoundError("auth0|123")

    @test_controller.get("/user-book-not-found")
    async def throw_user_book_not_found() -> None:
        raise UserBookNotFoundError(1)

    @test_controller.get("/unauthorized-user-book-access")
    async def throw_unauthorized_user_book_access_exception() -> None:
        raise UnauthorizedUserBookAccessError(1, "auth0|123", "auth0|999")

    @test_controller.get("/no-resource-found")
    async def throw_no_resource_found_exception() -> None:
        # Starlette's analogue of Spring's NoResourceFoundException.
        raise StarletteHTTPException(status_code=404)

    @test_controller.get("/generic-exception")
    async def throw_generic_exception() -> None:
        raise Exception()

    test_app = FastAPI(redirect_slashes=False)
    test_app.include_router(test_controller)
    register_exception_handlers(test_app)
    test_app.add_middleware(CatchAllExceptionMiddleware)
    return test_app


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    # The default transport re-raises unhandled exceptions, so a 500 proves the catch-all ran.
    transport = ASGITransport(app=_make_test_app())
    async with AsyncClient(transport=transport, base_url="http://localhost") as c:
        yield c


async def test_handle_user_not_found_returns_404_when_user_not_found_exception_thrown(
    client: AsyncClient,
) -> None:
    response = await client.get("/test/user-not-found")

    assert response.status_code == 404
    assert response.content == b""


async def test_handle_user_book_not_found_returns_404_when_user_book_not_found_exception_thrown(
    client: AsyncClient,
) -> None:
    response = await client.get("/test/user-book-not-found")

    assert response.status_code == 404
    assert response.content == b""


async def test_handle_unauthorized_user_book_access_returns_403_when_exception_thrown(
    client: AsyncClient,
) -> None:
    response = await client.get("/test/unauthorized-user-book-access")

    assert response.status_code == 403
    assert response.content == b""


async def test_handle_no_resource_found_returns_404_when_no_resource_found_exception_thrown(
    client: AsyncClient,
) -> None:
    response = await client.get("/test/no-resource-found")

    assert response.status_code == 404
    assert response.content == b""


async def test_handle_generic_exception_throws_500_when_generic_exception_thrown(
    client: AsyncClient,
) -> None:
    response = await client.get("/test/generic-exception")

    assert response.status_code == 500
    assert response.content == b""
