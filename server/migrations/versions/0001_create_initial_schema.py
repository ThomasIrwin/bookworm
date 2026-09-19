"""create initial schema

Ports the Flyway migration V1__create_initial_schema.sql.

Revision ID: 0001
Revises:
Create Date: 2026-09-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Databases created by the Spring Boot service already hold this schema, applied by Flyway and
    # recorded in flyway_schema_history. Adopt them as the baseline rather than recreating tables.
    if sa.inspect(op.get_bind()).has_table("books"):
        return

    # BigInteger primary keys render as BIGSERIAL on PostgreSQL, matching the Flyway DDL.
    op.create_table(
        "books",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("author", sa.String(255), nullable=False),
        sa.Column("description", sa.String(1000), nullable=True),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("auth0_id", sa.String(255), nullable=False, unique=True),
    )
    op.create_table(
        "user_books",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("book_id", sa.BigInteger(), sa.ForeignKey("books.id"), nullable=False),
        sa.Column("reading_status", sa.String(50), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("user_books")
    op.drop_table("users")
    op.drop_table("books")
