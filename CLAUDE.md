# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Behavioral Rules (Always Enforced)
- Do what has been asked; nothing more, nothing less
- NEVER create files unless they're absolutely necessary for achieving your goal
- ALWAYS prefer editing an existing file to creating a new one
- NEVER proactively create documentation files (*.md) or README files unless explicitly requested
- NEVER save working files, text/mds, or tests to the root folder
- Never continuously check status after spawning a swarm — wait for results
- ALWAYS read a file before editing it
- NEVER commit secrets, credentials, or .env files

## Project overview

Bookworm is a personal library assistant: a FastAPI backend (`server/`) and a React + TypeScript
frontend (`frontend/`), backed by PostgreSQL and Auth0 authentication.

## Project Architecture

- Follow Domain-Driven Design with bounded contexts
- Keep files under 500 lines
- Use typed interfaces for all public APIs
- Prefer TDD London School (mock-first) for new code
- Use event sourcing for state changes
- Ensure input validation at system boundaries

## Commands

All server commands run from `server/` via `uv` (installs into `server/.venv`).

```bash
uv sync --locked --all-groups        # install deps (does not add server/.env)
uv run uvicorn --factory app.main:create_app --reload --port 8080

uv run pytest                        # full suite
uv run pytest -m "not integration"   # skip tests needing Docker (testcontainers)
uv run pytest tests/userbooks        # one feature
uv run pytest tests/path/to_test.py::test_name   # single test
uv run pytest --cov=app

uv run ruff check .                  # lint
uv run ruff check --fix .            # lint with autofix
uv run ruff format .                 # format
uv run ruff format --check .         # format check (CI)
uv run mypy app                      # type check (strict mode)

uv run alembic upgrade head                              # apply migrations
uv run alembic revision --autogenerate -m "description"  # generate + review before applying
```

CI (`.github/workflows/ci.yaml`) runs `ruff check`, `ruff format --check`, `mypy app`, then
`pytest` (which starts PostgreSQL via Testcontainers, using Docker on the runner) — all from
`server/`, on PRs into `main`/`develop`.

Integration tests need Docker running locally; they spin up their own Postgres container and
never touch the dev database. Postgres for local dev is started separately via
`docker compose up -d postgres` (root `docker-compose.yaml`).

Frontend commands run from `frontend/`:

```bash
npm run dev       # Vite dev server on :3000
npm run build     # tsc -b && vite build
npm run lint      # eslint .
npm run preview
```

`automation/buildall-local.sh` (run from repo root) does the full local flow: starts Postgres,
runs the server test suite, builds and runs the server Docker image, waits for it to report
healthy, then starts the frontend dev server — useful as an end-to-end sanity check before a PR.

## Backend architecture (`server/app/`)

Organized by feature, each following the same layering:

- `router.py` — HTTP endpoints (FastAPI `APIRouter`), request/response wiring only
- `service.py` — business logic and transaction boundaries (services commit; repositories don't)
- `repository.py` — database queries (SQLAlchemy Core/ORM via `AsyncSession`)
- `entities.py` — SQLAlchemy ORM models
- `schemas.py` — Pydantic request/response models
- `exceptions.py` — domain errors, mapped to HTTP responses centrally

Feature packages: `auth/` (Auth0 JWT validation), `books/` (catalogue), `users/` (registration),
`userbooks/` (a user's library — add/list/remove), `health/` (`/actuator/health`, mirrors Spring
Actuator including its DB check), `exceptions/` (global handler mapping domain errors → HTTP
status, registered centrally in `app/main.py`).

Cross-cutting pieces:
- `app/main.py` — application factory (`create_app`); wires routers under the `/api/v1` prefix,
  middleware, and exception handlers. Middleware order matters: the *last* one added is
  outermost, so security headers wrap CORS, which wraps the 500 catch-all.
- `app/config.py` — `Settings` (pydantic-settings), reads `.env` / real env vars.
- `app/database.py` — async engine/sessionmaker (both `@lru_cache`d), one `AsyncSession` per
  request via `get_session`. Also defines `include_in_migrations`, an Alembic autogenerate hook
  that protects the `flyway_schema_history` table left behind by the old Java service — schemas
  created by that service are adopted, not recreated.
- `app/middleware.py` — pure ASGI middleware reimplementing what Spring Security/`@ControllerAdvice`
  used to provide: CORS (stricter/more explicit than Starlette's `CORSMiddleware` — rejects
  cross-origin requests from disallowed origins with a bare 403, preflight has no body), security
  headers, `HEAD`-as-`GET`, and a catch-all that turns unhandled exceptions into an empty 500.

Auth model: Auth0-issued RS256 JWTs, validated in `app/auth/dependencies.py` against the
configured issuer/audience with JWKS fetched via `PyJWKClient` (cached, off the event loop).
`CurrentAuth0Id` is the standard FastAPI dependency for "authenticated caller's Auth0 subject."
A handful of paths (`public_paths()`) are unauthenticated but still validate a bearer token if one
is sent, matching Spring Security's `permitAll` semantics.

All error responses have **empty bodies** — this mirrors the old service's
`ResponseEntity<Void>` handlers and is intentional, not an oversight.

## Testing (`server/tests/`)

Mirrors the `app/` layout. Two fixture tiers, defined in `tests/conftest.py`:

- **Unit/web tests**: build a fresh `FastAPI` app per test and override dependencies (the
  `override`/`authenticate`/`auth_client` fixtures), equivalent to `@WebMvcTest` +
  `@MockitoBean`. No Docker required.
- **Integration tests** (marked `@pytest.mark.integration`): run real PostgreSQL via
  Testcontainers (session-scoped container, Alembic migrated to `head` once), each test wrapped
  in a transaction that's rolled back afterward (`session_on` uses SAVEPOINTs so commits inside
  the code under test don't escape the test).

Notable test files: `test_request_parity.py` (Jackson/Spring MVC binding-parity fixtures — do not
"fix" these), `test_migrations.py`, `test_app_wiring.py`.

## Frontend (`frontend/src/`)

Vite + React 19 + TypeScript, Tailwind v4, Radix UI primitives, Auth0 React SDK for login,
`react-router-dom` for routing, `react-hook-form` for forms, `axios` for API calls
(`src/services/bookworm-api.ts` — base URL from `BOOKWORM_API_URL` env var, defaults to
`http://localhost:8080/api/v1`). Path alias `@/*` → `src/*`.

## Programming Style

- Prefer type-safe, explicit designs over object-heavy indirection. Use Python 3.12 `type`
  aliases, full annotations, and narrow `Protocol`s when a caller only needs a capability.
- Prefer functions and typed values before classes, and concrete classes before abstract base
  classes. Treat private-helper sprawl as a prompt to simplify the data flow.
- Use dataclasses for internal value objects and operation results; use Pydantic v2 at API,
  CLI, MCP, and persistence boundaries where validation and serialization matter.
- Keep async boundaries obvious. Resource-owning code should use context managers, propagate
  cancellation, and avoid hidden background work unless the lifecycle is explicit.
- Fail fast. Do not add silent fallback logic, broad exception swallowing, speculative
  `getattr`, or casts that hide an unclear model shape.
- Keep control flow simple and local. Push branching decisions up, keep leaf helpers focused,
  and name values after the domain concept they carry.
- Use evidence-first testing. Add or update meaningful regression tests for bugs and risky
  behavior, prefer real code paths over mocks, and run the narrowest command that proves the
  change before widening verification.
- Comments should explain why a branch, invariant, or constraint exists. Avoid comments that
  merely narrate obvious code.

### Code Change Guidelines

- **Full file read before edits**: Before editing any file, read it in full first to ensure complete context; partial reads lead to corrupted edits
- **Minimize diffs**: Prefer the smallest change that satisfies the request. Avoid unrelated refactors or style rewrites unless necessary for correctness
- **House style is canonical**: Follow the Programming Style section above for type-safe,
  fail-fast code; do not hide unclear models with speculative attributes, broad exception
  handling, casts, or unapproved fallback logic
- **No guessing**: Do not say "The issue is..." before you actually know what the issue is. Investigate first.