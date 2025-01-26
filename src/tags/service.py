from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.books.service import BookService, get_book_service
from src.db.models import Book, Tag

from .schemas import TagAddModel, TagCreateModel


server_error = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong"
)


class TagService:

    def __init__(self, book_service: BookService):
        self.book_service = book_service

    async def get_tags(self, session: AsyncSession):
        """Get all tags"""
        statement = select(Tag).order_by(Tag.created_at.desc())
        result = await session.exec(statement)
        return result.all()

    async def add_tags_to_book(
        self, book_id: str, tag_data: TagAddModel, session: AsyncSession
    ) -> Book:
        """Add tags to a book"""
        book = await self.book_service.get_book(id=book_id, session=session)
        print("book", book)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        for tag_item in tag_data.tags:
            result = await session.exec(select(Tag).where(Tag.name == tag_item.name))
            tag = result.one_or_none()
            if not tag:
                tag = Tag(name=tag_item.name)
            book.tags.append(tag)
        session.add(book)
        await session.commit()
        await session.refresh(book)
        return book

    async def get_tag_by_id(self, tag_id: str, session: AsyncSession):
        """Get tag by id"""
        statement = select(Tag).where(Tag.id == tag_id)
        result = await session.exec(statement)
        return result.first()

    async def add_tag(self, tag_data: TagCreateModel, session: AsyncSession):
        """Create a tag"""
        statement = select(Tag).where(Tag.name == tag_data.name)
        result = await session.exec(statement)
        if result.first():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Tag already exists"
            )

        new_tag = Tag(name=tag_data.name)
        session.add(new_tag)
        await session.commit()

        return new_tag

    async def update_tag(
        self, tag_id, tag_update_data: TagCreateModel, session: AsyncSession
    ):
        """Update a tag"""
        tag = await self.get_tag_by_id(tag_id, session)
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
            )

        for key, value in tag_update_data.model_dump().items():
            setattr(tag, key, value)

        await session.commit()
        await session.refresh(tag)
        return tag

    async def delete_tag(self, tag_id: str, session: AsyncSession):
        """Delete a tag"""
        tag = await self.get_tag_by_id(tag_id, session)
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tag does not exist"
            )
        await session.delete(tag)
        await session.commit()


def get_tag_service(book_service: BookService = Depends(get_book_service)):
    return TagService(book_service)
