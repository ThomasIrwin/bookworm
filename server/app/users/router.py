"""Mirrors users/UserController.java."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.auth.dependencies import CurrentAuth0Id
from app.users.service import UserService, get_user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/me",
    response_class=Response,
    responses={status.HTTP_201_CREATED: {"description": "User created"}},
)
async def get_or_save_current_user(
    auth0_id: CurrentAuth0Id,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> Response:
    user_was_created = await user_service.ensure_user_saved(auth0_id)
    return Response(status_code=status.HTTP_201_CREATED if user_was_created else status.HTTP_200_OK)
