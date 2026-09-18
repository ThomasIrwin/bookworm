#!/bin/sh
# Apply database migrations, then start the given command. Replaces Flyway's migrate-on-boot.
set -eu

alembic upgrade head

exec "$@"
