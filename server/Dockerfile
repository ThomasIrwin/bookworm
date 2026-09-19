# syntax=docker/dockerfile:1

# --- Build: resolve the locked dependencies into a virtual environment -----------------------
FROM python:3.12.14-slim-bookworm AS build

COPY --from=ghcr.io/astral-sh/uv:0.12.13 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

# Dependencies first, so source changes do not invalidate this layer.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev

COPY . .

# --- Runtime: same base image, no build tooling, unprivileged user -----------------------------
FROM python:3.12.14-slim-bookworm AS runtime

RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --no-create-home app

WORKDIR /app
COPY --from=build --chown=app:app /app /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    SERVER_DEV_PORT=8080

USER app
EXPOSE 8080

# python:slim has no curl; the probe hits the same endpoint automation/buildall-local.sh polls.
HEALTHCHECK --interval=10s --timeout=5s --start-period=20s --retries=5 \
    CMD ["python", "-c", "import os, sys, urllib.request; url = f\"http://127.0.0.1:{os.environ['SERVER_DEV_PORT']}/api/v1/actuator/health\"; sys.exit(0 if urllib.request.urlopen(url, timeout=3).status == 200 else 1)"]

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["sh", "-c", "exec uvicorn --factory app.main:create_app --host 0.0.0.0 --port \"$SERVER_DEV_PORT\" --proxy-headers --no-server-header"]
