# Bookworm Server

The Bookworm backend: a REST API for a personal library assistant, built with
[FastAPI](https://fastapi.tiangolo.com/), async SQLAlchemy 2.0 and PostgreSQL.
Authentication uses Auth0-issued JWT access tokens.

This service replaced an earlier Spring Boot implementation. Its HTTP contract is identical:
same paths, status codes, response shapes and headers. The React client in `frontend/` works
against it unchanged.

## Contents

- [Directory layout](#directory-layout)
- [API overview](#api-overview)
- [Prerequisites](#prerequisites)
- [Quick start](#quick-start)
- [Running in Docker](#running-in-docker)
- [Configuration](#configuration)
- [Database migrations](#database-migrations)
- [Testing and code quality](#testing-and-code-quality)
- [Troubleshooting](#troubleshooting)

## Directory layout

The code is organized by feature. Each feature package keeps the same separation of concerns:
a router handles HTTP, a service holds business logic and transaction boundaries, and a
repository handles database access.

```
server/
├── app/
│   ├── main.py              # Application factory: routers, middleware, exception handlers
│   ├── config.py            # Settings loaded from environment variables and .env
│   ├── database.py          # Async engine, per-request sessions, ORM base class
│   ├── middleware.py        # CORS, security headers, HEAD support, catch-all 500 handling
│   ├── auth/                # Auth0 JWT validation and the current-user dependency
│   ├── exceptions/          # Maps domain errors to HTTP status codes
│   ├── health/              # GET /actuator/health, including a database check
│   ├── books/               # Book catalogue
│   ├── users/               # User registration
│   └── userbooks/           # A user's library: add, list and remove books
│       ├── router.py        #   HTTP endpoints
│       ├── service.py       #   Business logic and transactions
│       ├── repository.py    #   Database queries
│       ├── entities.py      #   SQLAlchemy models
│       ├── schemas.py       #   Pydantic request and response models
│       ├── enums.py         #   ReadingStatus
│       └── exceptions.py    #   Domain errors
├── migrations/              # Alembic migration scripts
├── tests/                   # pytest suite, mirroring the app/ layout
├── alembic.ini              # Alembic configuration
├── docker-entrypoint.sh     # Applies migrations, then starts the server
├── Dockerfile               # Multi-stage production image
├── pyproject.toml           # Dependencies and tool configuration
├── uv.lock                  # Locked dependency versions
└── .env.example             # Template for local configuration
```

## API overview

All paths are served under the `/api/v1` prefix.

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/books/` | Token | List every book in the catalogue |
| GET | `/books/health` | Public | Returns `Application is healthy` as plain text |
| GET | `/actuator/health` | Public | Returns `{"status":"UP"}`, or 503 if the database is unreachable |
| POST | `/users/me` | Token | Registers the caller: 201 if new, 200 if already registered |
| GET | `/userbooks/` | Token | The caller's library |
| POST | `/userbooks/add-book` | Token | Adds a book to the caller's library and returns the updated library |
| DELETE | `/userbooks/delete-book/{id}` | Token | Removes a book: 204, or 403 if it belongs to someone else, or 404 |

Authenticated routes need an `Authorization: Bearer <token>` header carrying an Auth0 access
token for the audience `http://localhost:8080/api/v1`. Error responses have empty bodies.

Reading status is asymmetric by design. Requests send the constant, such as `IN_PROGRESS`.
Responses return the display name, such as `In Progress`.

## Prerequisites

| Tool | Version | Used for |
|---|---|---|
| Python | 3.12 | Running the server locally |
| [uv](https://docs.astral.sh/uv/) | 0.12 or later | Installing dependencies and running commands |
| Docker with Compose | Recent | PostgreSQL, integration tests and the container image |

Install uv if you don't have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Open a new terminal and confirm uv is on your `PATH`:

```bash
uv --version
```

If you see `uv: command not found`, the installer's directory (usually `~/.local/bin`) isn't on
your `PATH`. Add it to your shell's startup file, then open a new terminal. For bash:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

## Quick start

Run these steps to start the API locally with hot reload. Commands run from the `server/`
directory unless noted otherwise.

1. **Start PostgreSQL.** This runs from the repository root, where `docker-compose.yaml` lives.

   ```bash
   cd ..
   docker compose up -d postgres
   cd server
   ```

2. **Create your local configuration.** The example file points at `localhost`, which is right
   for running the server directly on your machine.

   ```bash
   cp .env.example .env
   ```

   To run the server in Docker instead, including through `automation/buildall-local.sh`, the
   database host must be `bookworm-db`. See [Running in Docker](#running-in-docker).

3. **Install dependencies.** This creates `.venv/` with the exact versions in `uv.lock`,
   including development tools.

   ```bash
   uv sync --locked --all-groups
   ```

4. **Apply database migrations.**

   ```bash
   uv run alembic upgrade head
   ```

5. **Start the server.**

   ```bash
   uv run uvicorn --factory app.main:create_app --reload --port 8080
   ```

6. **Check that it's running.**

   ```bash
   curl http://localhost:8080/api/v1/books/health
   curl http://localhost:8080/api/v1/actuator/health
   ```

   The first returns `Application is healthy`. The second returns `{"status":"UP"}`.

To browse interactive API docs, start the server with `ENABLE_DOCS=true` and open
<http://localhost:8080/api/v1/docs>.

## Running in Docker

### The whole stack

The build script at `automation/buildall-local.sh` starts PostgreSQL, runs the test suite,
builds and runs the server image, waits for it to report healthy, then starts the frontend.

```bash
# From the repository root
automation/buildall-local.sh
```

The script passes `server/.env` to the container. Inside the Docker network the database host
is `bookworm-db`, not `localhost`, so set this in `.env` before running it:

```dotenv
DATABASE_URL=postgresql+asyncpg://bookworm_dev:dev_pwd@bookworm-db:5432/bookworm
```

### The server image on its own

```bash
docker compose -f ../docker-compose.yaml up -d postgres
docker build -t bookworm-server .
docker run --rm --name bookworm-server \
  --network bookworm-network \
  --env-file .env \
  -p 8080:8080 \
  bookworm-server
```

The container applies pending migrations before it starts serving. It runs as an unprivileged
user and reports health through `/api/v1/actuator/health`.

## Configuration

Settings come from environment variables. For local runs they can also be set in `server/.env`.
Real environment variables take precedence over the file.

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | None | SQLAlchemy URL, e.g. `postgresql+asyncpg://user:password@host:5432/bookworm` |
| `SERVER_DEV_PORT` | No | `8080` | Port the container listens on |
| `AUTH0_ISSUER` | No | `https://dev-ulixqg71ihyco2h1.us.auth0.com/` | Expected token issuer, including the trailing slash |
| `AUTH0_AUDIENCE` | No | `http://localhost:8080/api/v1` | Expected token audience |
| `CORS_ALLOWED_ORIGINS` | No | `["http://localhost:3000"]` | JSON list of origins allowed to call the API |
| `ENABLE_DOCS` | No | `false` | Serves OpenAPI docs at `/api/v1/docs` when `true` |

`.env` is ignored by Git. Never commit real credentials.

## Database migrations

The schema is managed with Alembic. Migration scripts live in `migrations/versions/`.

```bash
uv run alembic upgrade head        # Apply all pending migrations
uv run alembic current             # Show the current revision
uv run alembic history             # List every revision
```

To change the schema, edit the models in the relevant `entities.py`, then generate a migration
and review it before applying:

```bash
uv run alembic revision --autogenerate -m "describe the change"
```

Databases created by the old Spring Boot service already have the schema. The first migration
detects this and adopts the existing tables without changing them or their data. Flyway's
`flyway_schema_history` table is left in place, and autogenerate ignores it.

## Testing and code quality

Integration tests start their own PostgreSQL container through Testcontainers, so Docker must
be running. They never touch your development database.

```bash
uv run pytest                          # Full suite
uv run pytest -m "not integration"     # Skip tests that need Docker
uv run pytest tests/userbooks          # One feature
uv run pytest --cov=app                # With a coverage report
```

These are the checks CI runs on every push to `develop` and every pull request to `main`:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy app
uv run pytest
```

Run `uv run ruff format .` to fix formatting and `uv run ruff check --fix .` to apply automatic
lint fixes.

## Troubleshooting

**`uv: command not found`, including from `automation/buildall-local.sh`.** uv is installed but
its directory isn't on your `PATH`. See [Prerequisites](#prerequisites).

**Startup fails with a validation error mentioning `database_url`.** `DATABASE_URL` isn't set.
Create `.env` from `.env.example`, or export the variable.

**The database connection is refused.** Check that PostgreSQL is running with
`docker compose ps`. Then check the host in `DATABASE_URL`: use `localhost` when running the
server directly and `bookworm-db` when running it in Docker.

**Every authenticated request returns 401.** Check the `WWW-Authenticate` response header,
which says why the token was rejected. Tokens must come from the configured Auth0 tenant and
carry the configured audience.

**uv warns that `VIRTUAL_ENV` does not match the project environment.** Tools such as pyenv set
`VIRTUAL_ENV`. The warning is harmless because uv still uses `server/.venv`.

**Port 8080 or 5432 is already in use.** Stop the other process, or run uvicorn with a different
`--port`. For the Docker Compose database, free port 5432.
