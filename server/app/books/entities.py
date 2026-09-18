from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))

    # Value equality on (title, author) preserves the Java entity's equals/hashCode contract,
    # which the add-book de-duplication and BookRepository tests rely on. It is safe for the ORM
    # because SQLAlchemy's identity map and unit of work track instances by state, not __eq__.
    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if type(other) is not type(self):
            return False
        assert isinstance(other, Book)
        return (self.title, self.author) == (other.title, other.author)

    def __hash__(self) -> int:
        return hash((self.title, self.author))

    def __repr__(self) -> str:
        return (
            f"Book{{id={self.id}, title='{self.title}', author='{self.author}', "
            f"description='{self.description}'}}"
        )
