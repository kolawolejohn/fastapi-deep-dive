from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import Book
from datetime import datetime
from src.books.schemas import BookCreateModel, BookUpdateModel


class BookService:

    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(Book.created_at.desc())
        result = await session.exec(statement)
        return result.all()

    async def get_user_books(self, user_id, session: AsyncSession):
        statement = (
            select(Book).where(Book.user_id == user_id).order_by(Book.created_at.desc())
        )
        result = await session.exec(statement)
        return result.all()

    async def get_book(self, id: str, session: AsyncSession):
        statement = select(Book).where(Book.id == id)
        result = await session.exec(statement)
        book = result.first()

        return book if book is not None else None

    async def create_book(
        self, data: BookCreateModel, user_id: str, session: AsyncSession
    ):

        data_dict = data.model_dump()
        if isinstance(data_dict.get("published_date"), str):
            data_dict["published_date"] = datetime.strptime(
                data_dict["published_date"], "%Y-%m-%d"
            )

        new_book = Book(**data_dict)
        new_book.user_id = user_id
        session.add(new_book)
        await session.commit()

        return new_book

    async def update_book(self, id: str, data: BookUpdateModel, session: AsyncSession):
        book_to_update = await self.get_book(id, session)
        book_update_dict = data.model_dump()

        if book_to_update is not None:
            for key, value in book_update_dict.items():
                setattr(book_to_update, key, value)

            await session.commit()

            return book_to_update
        else:
            return None

    async def delete_book(self, id: str, session: AsyncSession):
        book_to_delete = await self.get_book(id, session)
        if book_to_delete:
            await session.delete(book_to_delete)
            await session.commit()
            return True

        return False


async def get_book_service():
    return await BookService()
