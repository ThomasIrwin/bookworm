"""Auth0 JWT resource-server authentication. Mirrors config/SecurityConfig.java."""

import inspect
import logging
import re
from functools import lru_cache
from typing import Annotated, Final
from urllib.parse import urljoin

import jwt
from fastapi import Depends, HTTPException, Request, status
from starlette.concurrency import run_in_threadpool

from app.config import get_settings

logger = logging.getLogger(__name__)

_RFC6750_URI: Final = "https://tools.ietf.org/html/rfc6750#section-3.1"

# Spring Security's DefaultBearerTokenResolver pattern, matched case-insensitively.
_BEARER_PATTERN: Final = re.compile(r"Bearer (?P<token>[a-zA-Z0-9\-._~+/]+=*)", re.IGNORECASE)


def public_paths() -> frozenset[str]:
    """Paths permitted to all callers. Every other path under the API prefix is secured."""
    prefix = get_settings().api_prefix
    return frozenset({f"{prefix}/books/health", f"{prefix}/actuator/health"})


def _unauthorized(challenge: str = "Bearer") -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": challenge})


def _invalid_token(description: str) -> HTTPException:
    return _unauthorized(
        f'Bearer error="invalid_token", error_description="{description}", '
        f'error_uri="{_RFC6750_URI}"'
    )


def resolve_bearer_token(request: Request) -> str | None:
    """Extract the bearer token, or None when the request carries no bearer credentials."""
    authorization = request.headers.get("authorization")
    if authorization is None or not authorization.lower().startswith("bearer"):
        return None
    match = _BEARER_PATTERN.fullmatch(authorization)
    if match is None:
        raise _invalid_token("Bearer token is malformed")
    return match.group("token")


@lru_cache
def _jwk_client() -> jwt.PyJWKClient:
    issuer = get_settings().auth0_issuer
    return jwt.PyJWKClient(
        urljoin(issuer, ".well-known/jwks.json"),
        cache_keys=True,
        cache_jwk_set=True,
        lifespan=300,
        timeout=5,
    )


async def verify_bearer_token(token: str) -> str:
    """Validate signature, issuer, audience and expiry. Returns the `sub` claim."""
    settings = get_settings()
    try:
        # PyJWKClient performs blocking HTTP on a cache miss; keep it off the event loop.
        signing_key = await run_in_threadpool(_jwk_client().get_signing_key_from_jwt, token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=settings.auth0_algorithms,
            audience=settings.auth0_audience,
            issuer=settings.auth0_issuer,
            leeway=settings.jwt_leeway_seconds,
            options={"require": ["exp", "iss", "aud", "sub"]},
        )
    except jwt.ExpiredSignatureError:
        raise _invalid_token("Jwt expired") from None
    except jwt.InvalidAudienceError:
        raise _invalid_token("The token is missing the required audience") from None
    except jwt.InvalidIssuerError:
        raise _invalid_token("The iss claim is not valid") from None
    except jwt.PyJWKClientConnectionError:
        logger.warning("Could not retrieve the Auth0 JWK set")
        raise _invalid_token(
            "An error occurred while attempting to decode the Jwt: Couldn't retrieve remote JWK set"
        ) from None
    except jwt.PyJWTError as exc:
        logger.info("Rejected bearer token: %s", type(exc).__name__)
        raise _invalid_token(
            "An error occurred while attempting to decode the Jwt: Malformed token"
        ) from None

    subject = claims.get("sub")
    if not isinstance(subject, str) or not subject:
        raise _invalid_token(
            "An error occurred while attempting to decode the Jwt: Malformed token"
        )
    return subject


async def bearer_token(request: Request) -> str | None:
    return resolve_bearer_token(request)


async def get_current_auth0_id(token: Annotated[str | None, Depends(bearer_token)]) -> str:
    """Require an authenticated caller and return their Auth0 user id."""
    if token is None:
        raise _unauthorized()
    return await verify_bearer_token(token)


async def authenticate_if_bearer_present(
    token: Annotated[str | None, Depends(bearer_token)],
) -> None:
    """For public routes: Spring still rejects an invalid bearer token sent to a permitAll path."""
    if token is not None:
        await verify_bearer_token(token)


async def authenticate_request(request: Request) -> str:
    """Authenticate outside dependency injection, e.g. for requests that matched no route.

    Honours app.dependency_overrides so tests that substitute get_current_auth0_id behave the same
    on unrouted paths as on routed ones.
    """
    override = request.app.dependency_overrides.get(get_current_auth0_id)
    if override is not None:
        result = override()
        return str(await result) if inspect.isawaitable(result) else str(result)
    return await get_current_auth0_id(resolve_bearer_token(request))


CurrentAuth0Id = Annotated[str, Depends(get_current_auth0_id)]
