"""Mirrors the spring-boot-starter-actuator health endpoint, including its database indicator."""

import json
import logging
from typing import Annotated, Final

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import authenticate_if_bearer_present
from app.database import get_session

logger = logging.getLogger(__name__)

ACTUATOR_V3_JSON: Final = "application/vnd.spring-boot.actuator.v3+json"

router = APIRouter(prefix="/actuator", tags=["health"])


def _negotiate_media_type(accept: str) -> str:
    if ACTUATOR_V3_JSON not in accept and "application/json" in accept:
        return "application/json"
    return ACTUATOR_V3_JSON


@router.get(
    "/health",
    response_class=Response,
    dependencies=[Depends(authenticate_if_bearer_present)],
)
async def health(
    request: Request, session: Annotated[AsyncSession, Depends(get_session)]
) -> Response:
    try:
        await session.execute(text("SELECT 1"))
        health_status, status_code = "UP", status.HTTP_200_OK
    except Exception:
        logger.warning("Database health check failed", exc_info=True)
        health_status, status_code = "DOWN", status.HTTP_503_SERVICE_UNAVAILABLE

    return Response(
        content=json.dumps({"status": health_status}, separators=(",", ":")),
        status_code=status_code,
        media_type=_negotiate_media_type(request.headers.get("accept", "")),
    )
