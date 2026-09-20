"""Pure ASGI middleware."""

import logging
from typing import Final

from starlette.datastructures import MutableHeaders
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger(__name__)

# HSTS is only sent over HTTPS, so it is omitted here.
SECURITY_HEADERS: Final[dict[str, str]] = {
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "0",
    "Cache-Control": "no-cache, no-store, max-age=0, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0",
    "X-Frame-Options": "DENY",
}


class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                for name, value in SECURITY_HEADERS.items():
                    headers.setdefault(name, value)
            await send(message)

        await self.app(scope, receive, send_with_headers)


class HeadAsGetMiddleware:
    """Serve HEAD from the matching GET route with the body removed.

    FastAPI routes don't implicitly accept HEAD the way they accept GET, and Starlette's Response
    doesn't strip the body for a HEAD request either, so without this a HEAD request to a GET-only
    route is a 405.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["method"] != "HEAD":
            await self.app(scope, receive, send)
            return

        async def send_without_body(message: Message) -> None:
            if message["type"] == "http.response.body":
                if message.get("more_body", False):
                    return
                message = {"type": "http.response.body", "body": b"", "more_body": False}
            await send(message)

        await self.app({**scope, "method": "GET"}, receive, send_without_body)


class CatchAllExceptionMiddleware:
    """Turn any unhandled exception into a 500, and log it.

    An exception handler registered for `Exception` runs inside Starlette's ServerErrorMiddleware,
    which wraps the *entire* app, including every other middleware here — so a response built that
    way would skip CORS and the security headers below. Catching the exception in a middleware
    nested inside those instead means its response passes through them like any other.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        response_started = False

        async def tracking_send(message: Message) -> None:
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, receive, tracking_send)
        except Exception:
            logger.exception("Unhandled exception for %s %s", scope["method"], scope["path"])
            if response_started:
                raise
            response = JSONResponse({"detail": "Internal Server Error"}, status_code=500)
            await response(scope, receive, send)
