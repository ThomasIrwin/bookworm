"""Application settings. Mirrors src/main/resources/application.yaml."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # SQLAlchemy URL, e.g. postgresql+asyncpg://user:password@host:5432/bookworm
    database_url: str
    server_dev_port: int = 8080
    api_prefix: str = "/api/v1"
    enable_docs: bool = False

    cors_allowed_origins: list[str] = ["http://localhost:3000"]

    # The trailing slash on the issuer is significant: Auth0 emits it in the `iss` claim.
    auth0_issuer: str = "https://dev-ulixqg71ihyco2h1.us.auth0.com/"
    auth0_audience: str = "http://localhost:8080/api/v1"
    auth0_algorithms: list[str] = ["RS256"]
    # Matches Spring Security's default JwtTimestampValidator clock skew.
    jwt_leeway_seconds: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
