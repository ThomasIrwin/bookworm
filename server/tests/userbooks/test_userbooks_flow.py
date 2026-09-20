"""End-to-end flows through the real app, services and PostgreSQL, with only auth substituted.

This is where transactions, eager loading and the reading-status mapping run for real.
"""

from collections.abc import AsyncIterator, Callable
from typing import Any

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession

from app.database import get_session
from tests.conftest import session_on

pytestmark = pytest.mark.integration

ALICE = "auth0|alice"
BOB = "auth0|bob"


@pytest.fixture(autouse=True)
def database(app: FastAPI, connection: AsyncConnection) -> None:
    async def session_for_request() -> AsyncIterator[AsyncSession]:
        # A fresh session per request, as in production, sharing the test's rolled-back transaction.
        async with session_on(connection) as session:
            yield session

    app.dependency_overrides[get_session] = session_for_request


async def count(connection: AsyncConnection, sql: str, **params: Any) -> int:
    return int(await connection.scalar(text(sql), params) or 0)


async def register(client: AsyncClient, authenticate: Callable[[str], None], auth0_id: str) -> None:
    authenticate(auth0_id)
    response = await client.post("/users/me")
    assert response.status_code in (200, 201)


async def test_registering_a_user_returns_201_then_200(
    client: AsyncClient, authenticate: Callable[[str], None]
) -> None:
    authenticate(ALICE)

    assert (await client.post("/users/me")).status_code == 201
    assert (await client.post("/users/me")).status_code == 200


async def test_adding_books_returns_the_refreshed_library(
    client: AsyncClient, authenticate: Callable[[str], None], connection: AsyncConnection
) -> None:
    await register(client, authenticate, ALICE)

    first = await client.post(
        "/userbooks/add-book",
        json={"title": "Dune", "author": "Frank Herbert", "readingStatus": "IN_PROGRESS"},
    )
    assert first.status_code == 200
    [dune] = first.json()
    assert dune == {
        "id": dune["id"],
        "title": "Dune",
        "author": "Frank Herbert",
        "description": None,
        "readingStatus": "In Progress",
    }

    second = await client.post(
        "/userbooks/add-book",
        json={"title": "Dune", "author": "Frank Herbert", "readingStatus": "FINISHED"},
    )
    assert second.status_code == 200
    assert [ub["readingStatus"] for ub in second.json()] == ["In Progress", "Finished"]

    # The second add reuses the existing book rather than inserting a duplicate.
    assert await count(connection, "SELECT count(*) FROM books WHERE title = 'Dune'") == 1

    library = await client.get("/userbooks/")
    assert library.status_code == 200
    assert library.json() == second.json()


async def test_users_only_see_their_own_books(
    client: AsyncClient, authenticate: Callable[[str], None]
) -> None:
    await register(client, authenticate, ALICE)
    await client.post("/userbooks/add-book", json={"title": "Emma", "author": "Jane Austen"})
    await register(client, authenticate, BOB)

    response = await client.get("/userbooks/")

    assert response.status_code == 200
    assert response.json() == []


async def test_adding_a_book_for_an_unregistered_user_is_404_and_persists_nothing(
    client: AsyncClient, authenticate: Callable[[str], None], connection: AsyncConnection
) -> None:
    authenticate("auth0|ghost")

    response = await client.post(
        "/userbooks/add-book",
        json={"title": "Ghost Story", "author": "Nobody", "readingStatus": "FINISHED"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
    assert await count(connection, "SELECT count(*) FROM books WHERE title = 'Ghost Story'") == 0


async def test_failed_user_book_insert_rolls_back_the_new_book(
    client: AsyncClient, authenticate: Callable[[str], None], connection: AsyncConnection
) -> None:
    await register(client, authenticate, ALICE)

    # No readingStatus: the book insert succeeds, then user_books.reading_status NOT NULL fails.
    response = await client.post("/userbooks/add-book", json={"title": "Orphan", "author": "A"})

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
    assert await count(connection, "SELECT count(*) FROM books WHERE title = 'Orphan'") == 0


async def test_blank_title_is_rejected_and_persists_nothing(
    client: AsyncClient, authenticate: Callable[[str], None], connection: AsyncConnection
) -> None:
    await register(client, authenticate, ALICE)

    response = await client.post(
        "/userbooks/add-book",
        json={"title": "   ", "author": "A", "readingStatus": "WANT_TO_READ"},
    )

    assert response.status_code == 500
    assert await count(connection, "SELECT count(*) FROM user_books") == 0


async def test_deleting_books_enforces_ownership(
    client: AsyncClient, authenticate: Callable[[str], None]
) -> None:
    await register(client, authenticate, ALICE)
    added = await client.post(
        "/userbooks/add-book",
        json={"title": "Dune", "author": "Frank Herbert", "readingStatus": "PUT_DOWN"},
    )
    user_book_id = added.json()[0]["id"]

    await register(client, authenticate, BOB)
    forbidden = await client.delete(f"/userbooks/delete-book/{user_book_id}")
    assert forbidden.status_code == 403
    assert forbidden.json() == {"detail": "Forbidden"}

    authenticate(ALICE)
    deleted = await client.delete(f"/userbooks/delete-book/{user_book_id}")
    assert deleted.status_code == 204
    assert deleted.content == b""

    missing = await client.delete(f"/userbooks/delete-book/{user_book_id}")
    assert missing.status_code == 404

    assert (await client.get("/userbooks/")).json() == []


async def test_actuator_health_reports_up_with_a_live_database(client: AsyncClient) -> None:
    response = await client.get("/actuator/health")

    assert response.status_code == 200
    assert response.content == b'{"status":"UP"}'
