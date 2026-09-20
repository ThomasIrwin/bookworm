"""Liveness/readiness check, including a database connectivity indicator."""

import logging
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/actuator", tags=["health"])


class HealthStatus(BaseModel):
    status: Literal["UP", "DOWN"]


@router.get("/health")
async def health(session: Annotated[AsyncSession, Depends(get_session)]) -> JSONResponse:
    try:
        await session.execute(text("SELECT 1"))
        health_status, status_code = "UP", status.HTTP_200_OK
    except Exception:
        logger.warning("Database health check failed", exc_info=True)
        health_status, status_code = "DOWN", status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(HealthStatus(status=health_status).model_dump(), status_code=status_code)
