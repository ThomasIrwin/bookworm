from sqlalchemy import BigInteger, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym

from app.books.entities import Book
from app.database import Base
from app.userbooks.enums import ReadingStatus
from app.users.entities import User


class UserBook(Base):
    __tablename__ = "user_books"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    book_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("books.id"), nullable=False)

    # lazy="raise": async sessions cannot lazy-load, so every query must eager-load what it reads.
    # A missed case fails loudly instead of surfacing as MissingGreenlet in production.
    user: Mapped[User] = relationship(lazy="raise")
    book: Mapped[Book] = relationship(lazy="raise")

    # Stored by name in a plain VARCHAR(50), matching @Enumerated(EnumType.STRING) and the schema.
    reading_status: Mapped[ReadingStatus] = mapped_column(
        Enum(ReadingStatus, native_enum=False, length=50, create_constraint=False),
        nullable=False,
    )

    # The Java accessors were getStatus/setStatus over the readingStatus field.
    status = synonym("reading_status")
