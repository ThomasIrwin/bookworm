import logging
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.users.entities import User
from app.users.exceptions import UserNotFoundError
from app.users.repository import UserRepository

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, session: AsyncSession, user_repository: UserRepository) -> None:
        self._session = session
        self._user_repository = user_repository

    async def get_user(self, auth0_id: str) -> User:
        user = await self._user_repository.find_by_auth0_id(auth0_id)
        if user is None:
            raise UserNotFoundError(auth0_id)
        return user

    async def ensure_user_saved(self, auth0_id: str) -> bool:
        """Persist the user if new. Returns True when a row was created."""
        logger.debug("ensure_user_saved(): user id %s", auth0_id)
        result = await self._user_repository.upsert_user(auth0_id)
        await self._session.commit()
        return result != 0


def get_user_service(session: Annotated[AsyncSession, Depends(get_session)]) -> UserService:
    return UserService(session, UserRepository(session))
