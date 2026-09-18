from collections.abc import Callable
from typing import Annotated

from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict
from pydantic_core import PydanticCustomError


def _size(max_length: int) -> Callable[[str | None], str | None]:
    def validate(value: str | None) -> str | None:
        if value is not None and len(value) > max_length:
            raise PydanticCustomError(
                "size", "size must be between 0 and {max}", {"max": max_length}
            )
        return value

    return validate


def _not_blank(message: str) -> Callable[[str | None], str | None]:
    def validate(value: str | None) -> str | None:
        if value is None or not value.strip():
            raise PydanticCustomError("not_blank", message)
        return value

    return validate


# Runs before type validation so a None title reports "Title is required", as @NotBlank does.
_Title = Annotated[
    str, BeforeValidator(_not_blank("Title is required")), AfterValidator(_size(255))
]
_Author = Annotated[
    str, BeforeValidator(_not_blank("Author is required")), AfterValidator(_size(255))
]
_Description = Annotated[str | None, AfterValidator(_size(1000))]


class BookCreate(BaseModel):
    """Bean-validation constraints of the Java Book entity (@NotBlank, @Size)."""

    model_config = ConfigDict(from_attributes=True)

    title: _Title
    author: _Author
    description: _Description = None


class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None
    title: str | None
    author: str | None
    description: str | None
