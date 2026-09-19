"""Resource-server authentication, mirroring Spring Security's oauth2ResourceServer().jwt().

No test touches the network: tokens are signed with a local RSA key and the JWK client is stubbed.
"""

import time
from collections.abc import Callable
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, create_autospec

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from httpx import AsyncClient

from app.auth import dependencies
from app.config import get_settings
from app.userbooks.service import UserBooksService, get_user_books_service

RFC6750 = 'error_uri="https://tools.ietf.org/html/rfc6750#section-3.1"'
MALFORMED_TOKEN_CHALLENGE = (
    'Bearer error="invalid_token", error_description="An error occurred while attempting to '
    f'decode the Jwt: Malformed token", {RFC6750}'
)
MALFORMED_HEADER_CHALLENGE = (
    f'Bearer error="invalid_token", error_description="Bearer token is malformed", {RFC6750}'
)


@pytest.fixture(scope="module")
def signing_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


class StubJwkClient:
    def __init__(self, public_key: Any) -> None:
        self.public_key = public_key

    def get_signing_key_from_jwt(self, token: str) -> SimpleNamespace:
        jwt.get_unverified_header(token)  # malformed tokens fail here, as with PyJWKClient
        return SimpleNamespace(key=self.public_key)


@pytest.fixture
def jwks(monkeypatch: pytest.MonkeyPatch, signing_key: rsa.RSAPrivateKey) -> StubJwkClient:
    stub = StubJwkClient(signing_key.public_key())
    monkeypatch.setattr(dependencies, "_jwk_client", lambda: stub)
    return stub


@pytest.fixture
def make_token(signing_key: rsa.RSAPrivateKey) -> Callable[..., str]:
    def _make_token(key: Any = None, algorithm: str = "RS256", **claim_overrides: Any) -> str:
        settings = get_settings()
        now = int(time.time())
        claims: dict[str, Any] = {
            "iss": settings.auth0_issuer,
            "aud": settings.auth0_audience,
            "sub": "auth0|jwt-user",
            "iat": now,
            "exp": now + 300,
        }
        claims.update(claim_overrides)
        claims = {name: value for name, value in claims.items() if value is not None}
        return jwt.encode(
            claims, key or signing_key, algorithm=algorithm, headers={"kid": "test-key"}
        )

    return _make_token


@pytest.fixture
def user_books_service(override: Callable[[Callable[..., Any], Any], None]) -> MagicMock:
    service = create_autospec(UserBooksService, instance=True)
    service.get_all_user_books.return_value = []
    override(get_user_books_service, service)
    return service


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# --- Requests without usable bearer credentials ----------------------------------------------


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/books/"),
        ("GET", "/userbooks/"),
        ("POST", "/users/me"),
        ("POST", "/userbooks/add-book"),
        ("DELETE", "/userbooks/delete-book/1"),
    ],
)
async def test_secured_routes_return_401_without_token(
    client: AsyncClient, method: str, path: str
) -> None:
    response = await client.request(method, path)

    assert response.status_code == 401
    assert response.content == b""
    assert response.headers["www-authenticate"] == "Bearer"


async def test_non_bearer_scheme_is_treated_as_no_token(client: AsyncClient) -> None:
    response = await client.get("/userbooks/", headers={"Authorization": "Basic Zm9vOmJhcg=="})

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


async def test_empty_bearer_token_is_rejected_as_malformed(client: AsyncClient) -> None:
    response = await client.get("/userbooks/", headers={"Authorization": "Bearer "})

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == MALFORMED_HEADER_CHALLENGE


async def test_malformed_token_is_rejected_without_fetching_keys(client: AsyncClient) -> None:
    response = await client.get("/userbooks/", headers=bearer("abc.def.ghi"))

    assert response.status_code == 401
    assert response.content == b""
    assert response.headers["www-authenticate"] == MALFORMED_TOKEN_CHALLENGE


async def test_bearer_scheme_is_case_insensitive(client: AsyncClient) -> None:
    response = await client.get("/userbooks/", headers={"Authorization": "bearer abc.def.ghi"})

    assert response.headers["www-authenticate"] == MALFORMED_TOKEN_CHALLENGE


# --- Token validation ------------------------------------------------------------------------


@pytest.mark.usefixtures("jwks")
async def test_valid_token_authenticates_as_its_subject(
    client: AsyncClient, make_token: Callable[..., str], user_books_service: MagicMock
) -> None:
    response = await client.get("/userbooks/", headers=bearer(make_token()))

    assert response.status_code == 200
    user_books_service.get_all_user_books.assert_awaited_once_with("auth0|jwt-user")


@pytest.mark.usefixtures("jwks", "user_books_service")
async def test_audience_list_containing_the_api_audience_is_accepted(
    client: AsyncClient, make_token: Callable[..., str]
) -> None:
    audiences = [
        get_settings().auth0_audience,
        "https://dev-ulixqg71ihyco2h1.us.auth0.com/userinfo",
    ]

    response = await client.get("/userbooks/", headers=bearer(make_token(aud=audiences)))

    assert response.status_code == 200


@pytest.mark.usefixtures("jwks", "user_books_service")
async def test_token_expired_within_clock_skew_is_accepted(
    client: AsyncClient, make_token: Callable[..., str]
) -> None:
    token = make_token(exp=int(time.time()) - 30)

    response = await client.get("/userbooks/", headers=bearer(token))

    assert response.status_code == 200


@pytest.mark.usefixtures("jwks")
@pytest.mark.parametrize(
    ("claims", "description"),
    [
        ({"exp": int(time.time()) - 3600}, "Jwt expired"),
        ({"aud": "https://some-other-api"}, "The token is missing the required audience"),
        ({"iss": "https://attacker.example/"}, "The iss claim is not valid"),
        ({"sub": None}, "An error occurred while attempting to decode the Jwt: Malformed token"),
        ({"exp": None}, "An error occurred while attempting to decode the Jwt: Malformed token"),
    ],
)
async def test_invalid_claims_are_rejected(
    client: AsyncClient,
    make_token: Callable[..., str],
    claims: dict[str, Any],
    description: str,
) -> None:
    response = await client.get("/userbooks/", headers=bearer(make_token(**claims)))

    assert response.status_code == 401
    assert response.content == b""
    assert f'error_description="{description}"' in response.headers["www-authenticate"]


@pytest.mark.usefixtures("jwks")
async def test_token_signed_by_another_key_is_rejected(
    client: AsyncClient, make_token: Callable[..., str]
) -> None:
    other_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    response = await client.get("/userbooks/", headers=bearer(make_token(key=other_key)))

    assert response.status_code == 401


@pytest.mark.usefixtures("jwks")
async def test_unsigned_token_is_rejected(client: AsyncClient) -> None:
    settings = get_settings()
    claims = {
        "iss": settings.auth0_issuer,
        "aud": settings.auth0_audience,
        "sub": "auth0|forged",
        "exp": int(time.time()) + 300,
    }
    token = jwt.encode(claims, key=None, algorithm="none")

    response = await client.get("/userbooks/", headers=bearer(token))

    assert response.status_code == 401


async def test_unreachable_jwks_is_rejected(
    client: AsyncClient, make_token: Callable[..., str], monkeypatch: pytest.MonkeyPatch
) -> None:
    class UnreachableJwkClient:
        def get_signing_key_from_jwt(self, token: str) -> Any:
            raise jwt.PyJWKClientConnectionError("connection refused")

    monkeypatch.setattr(dependencies, "_jwk_client", UnreachableJwkClient)

    response = await client.get("/userbooks/", headers=bearer(make_token()))

    assert response.status_code == 401
    assert "Couldn't retrieve remote JWK set" in response.headers["www-authenticate"]


# --- Public routes ---------------------------------------------------------------------------


@pytest.mark.parametrize("path", ["/books/health", "/actuator/health"])
async def test_public_routes_reject_an_invalid_bearer_token(client: AsyncClient, path: str) -> None:
    response = await client.get(path, headers=bearer("abc.def.ghi"))

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == MALFORMED_TOKEN_CHALLENGE


async def test_public_route_ignores_non_bearer_credentials(client: AsyncClient) -> None:
    response = await client.get("/books/health", headers={"Authorization": "Basic Zm9vOmJhcg=="})

    assert response.status_code == 200


@pytest.mark.usefixtures("jwks")
async def test_public_route_accepts_a_valid_bearer_token(
    client: AsyncClient, make_token: Callable[..., str]
) -> None:
    response = await client.get("/books/health", headers=bearer(make_token()))

    assert response.status_code == 200


# --- Unrouted paths: Spring authenticated before dispatch -------------------------------------


@pytest.mark.parametrize("path", ["/nonexistent", "/books", "/books/health/", "/actuator"])
async def test_unrouted_secured_path_returns_401_without_token(
    client: AsyncClient, path: str
) -> None:
    response = await client.get(path)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.usefixtures("jwks")
async def test_unrouted_path_returns_404_with_valid_token(
    client: AsyncClient, make_token: Callable[..., str]
) -> None:
    response = await client.get("/nonexistent", headers=bearer(make_token()))

    assert response.status_code == 404
    assert response.content == b""


async def test_unrouted_path_outside_the_api_prefix_does_not_require_auth(
    app: Any,
) -> None:
    from httpx import ASGITransport

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as c:
        response = await c.get("/")

    assert response.status_code == 404
