"""Application wiring: routes, context path, headers, CORS and HTTP method handling."""

from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, create_autospec

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from app.books.service import BookService, get_book_service
from app.database import get_session
from app.middleware import SECURITY_HEADERS

FRONTEND_ORIGIN = "http://localhost:3000"


def assert_security_headers(headers: Any) -> None:
    for name, value in SECURITY_HEADERS.items():
        assert headers[name] == value


def test_route_table_matches_the_spring_request_mappings(app: FastAPI) -> None:
    # FastAPI keeps included routers nested, so read the effective table from its OpenAPI model.
    routes = {path: frozenset(operations) for path, operations in app.openapi()["paths"].items()}

    assert routes == {
        "/api/v1/actuator/health": frozenset({"get"}),
        "/api/v1/books/": frozenset({"get"}),
        "/api/v1/books/health": frozenset({"get"}),
        "/api/v1/users/me": frozenset({"post"}),
        "/api/v1/userbooks/": frozenset({"get"}),
        "/api/v1/userbooks/add-book": frozenset({"post"}),
        "/api/v1/userbooks/delete-book/{user_book_id}": frozenset({"delete"}),
    }


@pytest.mark.parametrize("path", ["/books", "/userbooks"])
async def test_missing_trailing_slash_is_not_redirected(
    auth_client: AsyncClient, path: str
) -> None:
    response = await auth_client.get(path)

    assert response.status_code == 404
    assert "location" not in response.headers


@pytest.mark.parametrize("path", ["/docs", "/openapi.json", "/redoc"])
async def test_api_docs_are_disabled_by_default(auth_client: AsyncClient, path: str) -> None:
    response = await auth_client.get(path)

    assert response.status_code == 404


async def test_books_health_is_plain_text(client: AsyncClient) -> None:
    response = await client.get("/books/health")

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert response.text == "Application is healthy"


# --- Security headers ------------------------------------------------------------------------


async def test_security_headers_on_success(client: AsyncClient) -> None:
    assert_security_headers((await client.get("/books/health")).headers)


async def test_security_headers_on_unauthorized(client: AsyncClient) -> None:
    assert_security_headers((await client.get("/userbooks/")).headers)


async def test_security_headers_on_not_found(auth_client: AsyncClient) -> None:
    assert_security_headers((await auth_client.get("/nonexistent")).headers)


async def test_unexpected_error_returns_500_with_headers(
    auth_client: AsyncClient, override: Callable[[Callable[..., Any], Any], None]
) -> None:
    service = create_autospec(BookService, instance=True)
    service.get_all_books.side_effect = RuntimeError("boom")
    override(get_book_service, service)

    response = await auth_client.get("/books/", headers={"Origin": FRONTEND_ORIGIN})

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
    assert_security_headers(response.headers)
    assert response.headers["access-control-allow-origin"] == FRONTEND_ORIGIN


# --- CORS ------------------------------------------------------------------------------------


async def test_cors_preflight_from_frontend_is_allowed(client: AsyncClient) -> None:
    response = await client.options(
        "/userbooks/",
        headers={
            "Origin": FRONTEND_ORIGIN,
            "Access-Control-Request-Method": "DELETE",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )

    assert response.status_code == 200
    assert response.content == b"OK"
    assert response.headers["access-control-allow-origin"] == FRONTEND_ORIGIN
    assert response.headers["access-control-allow-credentials"] == "true"
    assert (
        response.headers["access-control-allow-methods"] == "GET, HEAD, POST, PUT, DELETE, OPTIONS"
    )
    # The configured allow-list, merged with CORSMiddleware's safelisted headers, not an echo of
    # whatever the client asked for.
    assert response.headers["access-control-allow-headers"] == (
        "Accept, Accept-Language, Authorization, Content-Language, Content-Type"
    )
    assert response.headers["access-control-max-age"] == "1800"
    assert_security_headers(response.headers)


async def test_cors_simple_request_from_frontend_carries_credentials_headers(
    client: AsyncClient,
) -> None:
    response = await client.get("/books/health", headers={"Origin": FRONTEND_ORIGIN})

    assert response.headers["access-control-allow-origin"] == FRONTEND_ORIGIN
    assert response.headers["access-control-allow-credentials"] == "true"


async def test_cors_simple_request_from_unknown_origin_has_no_cors_headers(
    client: AsyncClient,
) -> None:
    # The browser enforces CORS client-side; a disallowed-origin request still reaches the app
    # and gets its normal response, just without the header that would let the browser accept it.
    response = await client.get("/books/health", headers={"Origin": "http://evil.example"})

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers
    assert_security_headers(response.headers)


async def test_cors_preflight_from_unknown_origin_is_rejected(client: AsyncClient) -> None:
    response = await client.options(
        "/books/health",
        headers={"Origin": "http://evil.example", "Access-Control-Request-Method": "GET"},
    )

    assert response.status_code == 400
    assert response.content == b"Disallowed CORS origin"
    assert "access-control-allow-origin" not in response.headers
    assert_security_headers(response.headers)


async def test_cors_preflight_for_a_method_not_allowed_is_rejected(client: AsyncClient) -> None:
    response = await client.options(
        "/userbooks/",
        headers={"Origin": FRONTEND_ORIGIN, "Access-Control-Request-Method": "PATCH"},
    )

    assert response.status_code == 400
    assert response.content == b"Disallowed CORS method"


async def test_cors_origin_matching_is_case_sensitive(client: AsyncClient) -> None:
    response = await client.get("/books/health", headers={"Origin": "HTTP://LOCALHOST:3000"})

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


async def test_request_from_an_origin_not_on_the_allow_list_has_no_cors_headers(
    client: AsyncClient,
) -> None:
    response = await client.get("/books/health", headers={"Origin": "http://localhost:8080"})

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


# --- HTTP methods ----------------------------------------------------------------------------


async def test_head_is_served_by_the_get_route_without_a_body(client: AsyncClient) -> None:
    response = await client.head("/books/health")

    assert response.status_code == 200
    assert response.content == b""
    assert response.headers["content-length"] == "22"
    assert response.headers["content-type"] == "text/plain; charset=utf-8"


async def test_head_on_a_post_only_route_is_method_not_allowed(client: AsyncClient) -> None:
    # A method mismatch is decided by the routing layer itself, before any dependency (including
    # auth) runs, so no token is needed to observe it.
    response = await client.head("/userbooks/add-book")

    assert response.status_code == 405
    assert response.headers["allow"] == "POST"
    assert response.content == b""  # HEAD never carries a body, even for an error response.


@pytest.mark.parametrize(
    ("path", "allow"),
    [
        ("/books/health", "GET"),
        ("/userbooks/", "GET"),
        ("/userbooks/add-book", "POST"),
    ],
)
async def test_plain_options_is_method_not_allowed(
    client: AsyncClient, path: str, allow: str
) -> None:
    response = await client.options(path)

    assert response.status_code == 405
    assert response.headers["allow"] == allow
    assert response.json() == {"detail": "Method Not Allowed"}


@pytest.mark.parametrize(
    ("method", "path", "allow"),
    [("PUT", "/userbooks/", "GET"), ("GET", "/userbooks/add-book", "POST")],
)
async def test_unsupported_method_is_method_not_allowed(
    client: AsyncClient, method: str, path: str, allow: str
) -> None:
    response = await client.request(method, path)

    assert response.status_code == 405
    assert response.headers["allow"] == allow
    assert response.json() == {"detail": "Method Not Allowed"}


async def test_unsupported_method_on_public_path_is_method_not_allowed(
    client: AsyncClient,
) -> None:
    response = await client.post("/books/health")

    assert response.status_code == 405


# --- Actuator health -------------------------------------------------------------------------


@pytest.fixture
def db_session(override: Callable[[Callable[..., Any], Any], None]) -> MagicMock:
    session = create_autospec(AsyncSession, instance=True)
    override(get_session, session)
    return session


@pytest.mark.usefixtures("db_session")
async def test_actuator_health_is_up(client: AsyncClient) -> None:
    response = await client.get("/actuator/health")

    assert response.status_code == 200
    assert response.content == b'{"status":"UP"}'
    assert response.headers["content-type"] == "application/json"


async def test_actuator_health_is_down_when_database_is_unreachable(
    client: AsyncClient, db_session: MagicMock
) -> None:
    db_session.execute.side_effect = OperationalError("SELECT 1", {}, Exception("refused"))

    response = await client.get("/actuator/health")

    assert response.status_code == 503
    assert response.content == b'{"status":"DOWN"}'
