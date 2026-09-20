"""Application factory.

Run with: uvicorn --factory app.main:create_app
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.books.router import router as books_router
from app.config import get_settings
from app.database import get_engine
from app.exceptions.handlers import register_exception_handlers
from app.health.router import router as health_router
from app.middleware import (
    CatchAllExceptionMiddleware,
    HeadAsGetMiddleware,
    SecurityHeadersMiddleware,
)
from app.userbooks.router import router as userbooks_router
from app.users.router import router as users_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    if get_engine.cache_info().currsize:
        await get_engine().dispose()


def create_app() -> FastAPI:
    settings = get_settings()
    docs_enabled = settings.enable_docs

    app = FastAPI(
        title="Bookworm",
        description="A Personal Library Assistant",
        version="0.0.1",
        lifespan=lifespan,
        # Paths are matched literally: /books/ and /books are distinct, no redirect between them.
        redirect_slashes=False,
        openapi_url=f"{settings.api_prefix}/openapi.json" if docs_enabled else None,
        docs_url=f"{settings.api_prefix}/docs" if docs_enabled else None,
        redoc_url=None,
    )
    app.router.redirect_slashes = False

    # Replaces server.servlet.context-path.
    api = APIRouter(prefix=settings.api_prefix)
    api.include_router(health_router)
    api.include_router(books_router)
    api.include_router(users_router)
    api.include_router(userbooks_router)
    app.include_router(api)

    register_exception_handlers(app)

    # The last middleware added is outermost: security headers wrap CORS, which wraps the 500
    # catch-all, which wraps HEAD handling, so even a crash, a CORS-rejected preflight, and a HEAD
    # response all carry the outer two.
    app.add_middleware(HeadAsGetMiddleware)
    app.add_middleware(CatchAllExceptionMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_methods=["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
        allow_credentials=True,
        max_age=1800,
    )
    app.add_middleware(SecurityHeadersMiddleware)

    return app
