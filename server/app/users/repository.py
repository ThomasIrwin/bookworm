from typing import Any, cast

from sqlalchemy import CursorResult, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.entities import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, user: User) -> User:
        self._session.add(user)
        await self._session.flush()
        return user

    async def find_all(self) -> list[User]:
        result = await self._session.scalars(select(User).order_by(User.id))
        return list(result)

    async def find_by_auth0_id(self, auth0_id: str) -> User | None:
        result = await self._session.scalars(select(User).where(User.auth0_id == auth0_id))
        return result.one_or_none()

    async def upsert_user(self, auth0_id: str) -> int:
        """Insert the user if absent. Returns the affected row count: 1 if inserted, 0 if not."""
        result = await self._session.execute(
            text("INSERT INTO users (auth0_id) VALUES (:auth0_id) ON CONFLICT DO NOTHING"),
            {"auth0_id": auth0_id},
        )
        return cast(CursorResult[Any], result).rowcount
