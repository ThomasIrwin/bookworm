from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from app.userbooks.enums import ReadingStatus


def _coerce_scalar_to_string(value: object) -> object:
    """Jackson binds JSON scalars into String fields: 123 becomes "123", true becomes "true"."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int | float):
        return str(value)
    return value


def _reading_status_from_ordinal(value: object) -> object:
    """Jackson also binds an enum from its ordinal, given as a JSON number or a numeric string."""
    if isinstance(value, str) and value.isascii() and value.isdigit():
        value = int(value)
    if isinstance(value, int) and not isinstance(value, bool):
        members = list(ReadingStatus)
        if 0 <= value < len(members):
            return members[value]
    return value


_JacksonString = Annotated[str | None, BeforeValidator(_coerce_scalar_to_string)]


class AddBookRequest(BaseModel):
    """Inbound readingStatus is the enum constant, e.g. IN_PROGRESS.

    Every field is optional because the Java record accepted nulls; missing values surface in the
    service (404 for an unknown user, 500 on persist) exactly as they did before.
    """

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    title: _JacksonString = None
    author: _JacksonString = None
    description: _JacksonString = None
    reading_status: Annotated[
        ReadingStatus | None, BeforeValidator(_reading_status_from_ordinal)
    ] = Field(default=None, alias="readingStatus")


class UserBookDTO(BaseModel):
    """Outbound readingStatus is the display name, e.g. "In Progress"."""

    model_config = ConfigDict(
        validate_by_name=True, validate_by_alias=True, serialize_by_alias=True
    )

    id: int | None
    title: str | None
    author: str | None
    description: str | None
    reading_status: str | None = Field(alias="readingStatus")
