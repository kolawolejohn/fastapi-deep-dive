from datetime import date, datetime
from typing import Optional, TYPE_CHECKING
import uuid
from sqlalchemy import Column
from sqlmodel import Field, Relationship, SQLModel
import sqlalchemy.dialects.postgresql as pg

if TYPE_CHECKING:
    from src.auth.models import User


class Book(SQLModel, table=True):
    __tablename__ = "books"

    id: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, nullable=False, default=datetime.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, nullable=False, default=datetime.now())
    )
    user: Optional["User"] = Relationship(back_populates="books")


def __repr__(self):
    return f"<Book {self.title}>"
