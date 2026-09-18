"""Application wiring: routes, context path, headers, CORS and HTTP method handling.

Expected values come from responses recorded against the Spring Boot service before migration.
"""

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
    assert response.headers["content-type"] == "text/plain;charset=UTF-8"
    assert response.text == "Application is healthy"


# --- Security headers ------------------------------------------------------------------------


async def test_security_headers_on_success(client: AsyncClient) -> None:
    assert_security_headers((await client.get("/books/health")).headers)


async def test_security_headers_on_unauthorized(client: AsyncClient) -> None:
    assert_security_headers((await client.get("/userbooks/")).headers)


async def test_security_headers_on_not_found(auth_client: AsyncClient) -> None:
    assert_security_headers((await auth_client.get("/nonexistent")).headers)


async def test_unexpected_error_returns_empty_500_with_headers(
    auth_client: AsyncClient, override: Callable[[Callable[..., Any], Any], None]
) -> None:
    service = create_autospec(BookService, instance=True)
    service.get_all_books.side_effect = RuntimeError("boom")
    override(get_book_service, service)

    response = await auth_client.get("/books/", headers={"Origin": FRONTEND_ORIGIN})

    assert response.status_code == 500
    assert response.content == b""
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
    assert response.content == b""
    assert "content-type" not in response.headers
    assert response.headers["access-control-allow-origin"] == FRONTEND_ORIGIN
    assert response.headers["access-control-allow-credentials"] == "true"
    assert response.headers["access-control-allow-methods"] == "GET,POST,PUT,DELETE,OPTIONS"
    assert response.headers["access-control-allow-headers"] == "authorization, content-type"
    assert response.headers["access-control-max-age"] == "1800"
    assert_security_headers(response.headers)


async def test_cors_simple_request_from_frontend_carries_credentials_headers(
    client: AsyncClient,
) -> None:
    response = await client.get("/books/health", headers={"Origin": FRONTEND_ORIGIN})

    assert response.headers["access-control-allow-origin"] == FRONTEND_ORIGIN
    assert response.headers["access-control-allow-credentials"] == "true"


@pytest.mark.parametrize(
    ("method", "extra_headers"),
    [("GET", {}), ("OPTIONS", {"Access-Control-Request-Method": "GET"})],
    ids=["simple", "preflight"],
)
async def test_cors_request_from_unknown_origin_is_rejected(
    client: AsyncClient, method: str, extra_headers: dict[str, str]
) -> None:
    response = await client.request(
        method, "/books/health", headers={"Origin": "http://evil.example", **extra_headers}
    )

    assert response.status_code == 403
    assert response.content == b"Invalid CORS request"
    assert "access-control-allow-origin" not in response.headers
    assert_security_headers(response.headers)


async def test_cors_preflight_for_a_method_not_allowed_is_rejected(client: AsyncClient) -> None:
    response = await client.options(
        "/userbooks/",
        headers={"Origin": FRONTEND_ORIGIN, "Access-Control-Request-Method": "PATCH"},
    )

    assert response.status_code == 403


async def test_cors_origin_matching_ignores_case(client: AsyncClient) -> None:
    response = await client.get("/books/health", headers={"Origin": "HTTP://LOCALHOST:3000"})

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "HTTP://LOCALHOST:3000"


async def test_same_origin_request_is_not_treated_as_cors(client: AsyncClient) -> None:
    response = await client.get("/books/health", headers={"Origin": "http://localhost:8080"})

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


async def test_every_response_varies_on_cors_request_headers(client: AsyncClient) -> None:
    response = await client.get("/userbooks/")

    assert response.headers.get_list("vary") == [
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ]


# --- HTTP methods ----------------------------------------------------------------------------


async def test_head_is_served_by_the_get_route_without_a_body(client: AsyncClient) -> None:
    response = await client.head("/books/health")

    assert response.status_code == 200
    assert response.content == b""
    assert response.headers["content-length"] == "22"
    assert response.headers["content-type"] == "text/plain;charset=UTF-8"


async def test_head_on_a_post_only_route_is_a_server_error(auth_client: AsyncClient) -> None:
    response = await auth_client.head("/userbooks/add-book")

    assert response.status_code == 500


@pytest.mark.parametrize(
    ("path", "allow"),
    [
        ("/books/health", "GET,HEAD,OPTIONS"),
        ("/userbooks/", "GET,HEAD,OPTIONS"),
        ("/userbooks/add-book", "POST,OPTIONS"),
    ],
)
async def test_plain_options_lists_supported_methods(
    auth_client: AsyncClient, path: str, allow: str
) -> None:
    response = await auth_client.options(path)

    assert response.status_code == 200
    assert response.content == b""
    assert response.headers["allow"] == allow
    assert response.headers["accept-patch"] == ""


async def test_plain_options_on_secured_path_requires_auth(client: AsyncClient) -> None:
    response = await client.options("/userbooks/")

    assert response.status_code == 401


@pytest.mark.parametrize(
    ("method", "path"), [("PUT", "/userbooks/"), ("GET", "/userbooks/add-book")]
)
async def test_unsupported_method_is_a_server_error(
    auth_client: AsyncClient, method: str, path: str
) -> None:
    response = await auth_client.request(method, path)

    assert response.status_code == 500
    assert response.content == b""
    assert "allow" not in response.headers


async def test_unsupported_method_on_public_path_is_a_server_error(client: AsyncClient) -> None:
    response = await client.post("/books/health")

    assert response.status_code == 500


async def test_unsupported_method_on_secured_path_requires_auth_first(client: AsyncClient) -> None:
    response = await client.put("/userbooks/")

    assert response.status_code == 401


# --- Actuator health -------------------------------------------------------------------------


@pytest.fixture
def db_session(override: Callable[[Callable[..., Any], Any], None]) -> MagicMock:
    session = create_autospec(AsyncSession, instance=True)
    override(get_session, session)
    return session


@pytest.mark.usefixtures("db_session")
@pytest.mark.parametrize(
    ("accept", "content_type"),
    [
        ("*/*", "application/vnd.spring-boot.actuator.v3+json"),
        ("application/json", "application/json"),
        ("application/json, text/plain, */*", "application/json"),
    ],
)
async def test_actuator_health_is_up(client: AsyncClient, accept: str, content_type: str) -> None:
    response = await client.get("/actuator/health", headers={"Accept": accept})

    assert response.status_code == 200
    assert response.content == b'{"status":"UP"}'
    assert response.headers["content-type"] == content_type


async def test_actuator_health_is_down_when_database_is_unreachable(
    client: AsyncClient, db_session: MagicMock
) -> None:
    db_session.execute.side_effect = OperationalError("SELECT 1", {}, Exception("refused"))

    response = await client.get("/actuator/health")

    assert response.status_code == 503
    assert response.content == b'{"status":"DOWN"}'
