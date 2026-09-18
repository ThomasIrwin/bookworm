from enum import StrEnum
from typing import Final


class ReadingStatus(StrEnum):
    # Values equal names: the API accepts and the database stores the constant, e.g. IN_PROGRESS.
    WANT_TO_READ = "WANT_TO_READ"
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"
    PUT_DOWN = "PUT_DOWN"

    @property
    def display_name(self) -> str:
        return _DISPLAY_NAMES[self]


_DISPLAY_NAMES: Final[dict[ReadingStatus, str]] = {
    ReadingStatus.WANT_TO_READ: "Want to Read",
    ReadingStatus.IN_PROGRESS: "In Progress",
    ReadingStatus.FINISHED: "Finished",
    ReadingStatus.PUT_DOWN: "Put Down",
}
