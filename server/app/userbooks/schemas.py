from pydantic import BaseModel, ConfigDict, Field

from app.userbooks.enums import ReadingStatus


class AddBookRequest(BaseModel):
    """Inbound readingStatus is the enum constant, e.g. IN_PROGRESS."""

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    description: str | None = None
    reading_status: ReadingStatus | None = Field(default=None, alias="readingStatus")


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
