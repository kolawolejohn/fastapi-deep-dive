from datetime import datetime
import uuid
from sqlalchemy import Column
from sqlmodel import Field, SQLModel
import sqlalchemy.dialects.postgresql as pg


class Book(SQLModel, table=True):
    __tablename__ = "books"

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4()
        )
    )
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str
    created_at: datetime = Field(
        Column(pg.TIMESTAMP, nullable=False, default=datetime.now())
    )
    updated_at: datetime = Field(
        Column(pg.TIMESTAMP, nullable=False, default=datetime.now())
    )


def __repr__(self):
    return f"<Book {self.title}>"
