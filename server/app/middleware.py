"""Pure ASGI middleware. Mirrors behaviour Spring Security and @ControllerAdvice provided."""

import logging
from collections.abc import Sequence
from typing import Final
from urllib.parse import urlsplit

from starlette.datastructures import Headers, MutableHeaders
from starlette.responses import Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger(__name__)

# Spring Security's default response headers (HSTS is only sent over HTTPS, so it is omitted).
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


_CORS_VARY: Final = ("Origin", "Access-Control-Request-Method", "Access-Control-Request-Headers")


def _append_cors_vary(headers: MutableHeaders) -> None:
    present = {
        token.strip().lower() for value in headers.getlist("vary") for token in value.split(",")
    }
    for name in _CORS_VARY:
        if name.lower() not in present:
            headers.append("Vary", name)


def _default_port(scheme: str) -> int:
    return 443 if scheme in ("https", "wss") else 80


def _is_same_origin(scope: Scope, request_headers: Headers, origin: str) -> bool:
    host = request_headers.get("host")
    if host is None:
        return False
    try:
        origin_url = urlsplit(origin)
        request_url = urlsplit(f"{scope.get('scheme', 'http')}://{host}")
        return (
            origin_url.scheme == request_url.scheme
            and origin_url.hostname == request_url.hostname
            and (origin_url.port or _default_port(origin_url.scheme))
            == (request_url.port or _default_port(request_url.scheme))
        )
    except ValueError:
        return False


class CorsMiddleware:
    """CORS handling equivalent to Spring's CorsFilter and DefaultCorsProcessor.

    It differs from Starlette's CORSMiddleware in ways clients can observe. Requests from
    origins that are not allowed are rejected with 403 before reaching the application.
    Preflight responses have no body. Every response varies on the CORS request headers.
    All requested headers are allowed, as with allowedHeaders("*").
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        allowed_origins: Sequence[str],
        allowed_methods: Sequence[str],
        allow_credentials: bool,
        max_age: int,
    ) -> None:
        self.app = app
        self.allowed_origins = frozenset(origin.rstrip("/").lower() for origin in allowed_origins)
        self.allowed_methods = tuple(allowed_methods)
        self.allow_credentials = allow_credentials
        self.max_age = max_age

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_headers = Headers(scope=scope)
        origin = request_headers.get("origin")
        cors_headers: list[tuple[str, str]] = []

        if origin is not None and not _is_same_origin(scope, request_headers, origin):
            preflight = (
                scope["method"] == "OPTIONS" and "access-control-request-method" in request_headers
            )
            allowed = self._cors_headers(origin, scope["method"], request_headers, preflight)
            if allowed is None:
                await self._respond(scope, receive, send, 403, b"Invalid CORS request", [])
                return
            if preflight:
                await self._respond(scope, receive, send, 200, b"", allowed)
                return
            cors_headers = allowed

        async def send_with_cors_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                _append_cors_vary(headers)
                for name, value in cors_headers:
                    headers[name] = value
            await send(message)

        await self.app(scope, receive, send_with_cors_headers)

    def _cors_headers(
        self, origin: str, method: str, request_headers: Headers, preflight: bool
    ) -> list[tuple[str, str]] | None:
        """The headers granting this CORS request, or None when it must be rejected."""
        if origin.rstrip("/").lower() not in self.allowed_origins:
            return None
        requested_method = request_headers["access-control-request-method"] if preflight else method
        if requested_method not in self.allowed_methods:
            return None

        headers = [("Access-Control-Allow-Origin", origin)]
        if preflight:
            headers.append(("Access-Control-Allow-Methods", ",".join(self.allowed_methods)))
            requested_headers = [
                name.strip()
                for value in request_headers.getlist("access-control-request-headers")
                for name in value.split(",")
                if name.strip()
            ]
            if requested_headers:
                headers.append(("Access-Control-Allow-Headers", ", ".join(requested_headers)))
        if self.allow_credentials:
            headers.append(("Access-Control-Allow-Credentials", "true"))
        if preflight:
            headers.append(("Access-Control-Max-Age", str(self.max_age)))
        return headers

    @staticmethod
    async def _respond(
        scope: Scope,
        receive: Receive,
        send: Send,
        status_code: int,
        body: bytes,
        headers: list[tuple[str, str]],
    ) -> None:
        response = Response(content=body, status_code=status_code)
        _append_cors_vary(response.headers)
        for name, value in headers:
            response.headers[name] = value
        await response(scope, receive, send)


class HeadAsGetMiddleware:
    """Serve HEAD from the matching GET route with the body removed, as servlet containers do."""

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
    """Turns any unhandled exception into an empty 500, like @ExceptionHandler(Exception.class).

    Implemented as middleware rather than an Exception handler because Starlette routes Exception
    handlers to ServerErrorMiddleware, which re-raises after responding.
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
            await Response(status_code=500)(scope, receive, send)
