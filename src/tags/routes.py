from typing import List

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession


from src.auth.dependencies import RoleChecker
from src.books.schemas import Book
from src.db.main import get_session

from .schemas import TagAddModel, TagCreateModel, TagModel
from .service import TagService, get_tag_service

tags_router = APIRouter()
user_role_checker = Depends(RoleChecker(["user", "admin"]))
admin_role_checker = Depends(RoleChecker(["admin"]))


@tags_router.get(
    "/",
    response_model=List[TagModel],
    dependencies=[user_role_checker],
)
async def get_all_tags(
    session: AsyncSession = Depends(get_session),
    tag_service: TagService = Depends(get_tag_service),
):
    tags = await tag_service.get_tags(session)
    return tags


@tags_router.post(
    "/",
    response_model=TagModel,
    status_code=status.HTTP_201_CREATED,
    dependencies=[admin_role_checker],
)
async def add_tag(
    tag_data: TagCreateModel,
    session: AsyncSession = Depends(get_session),
    tag_service: TagService = Depends(get_tag_service),
) -> TagModel:

    tag_added = await tag_service.add_tag(tag_data=tag_data, session=session)
    return tag_added


@tags_router.post(
    "/book/{book_id}/tags", response_model=Book, dependencies=[user_role_checker]
)
async def add_tags_to_book(
    book_id: str,
    tag_data: TagAddModel,
    session: AsyncSession = Depends(get_session),
    tag_service: TagService = Depends(get_tag_service),
) -> Book:

    book_with_tag = await tag_service.add_tags_to_book(
        book_id=book_id, tag_data=tag_data, session=session
    )

    return book_with_tag


@tags_router.put(
    "/{tag_id}", response_model=TagModel, dependencies=[admin_role_checker]
)
async def update_tag(
    tag_id: str,
    tag_update_data: TagCreateModel,
    session: AsyncSession = Depends(get_session),
    tag_service: TagService = Depends(get_tag_service),
) -> TagModel:

    updated_tag = await tag_service.update_tag(tag_id, tag_update_data, session)
    return updated_tag


@tags_router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[admin_role_checker],
)
async def delete_tag(
    tag_id: str,
    session: AsyncSession = Depends(get_session),
    tag_service: TagService = Depends(get_tag_service),
) -> None:
    deleted_tag = await tag_service.delete_tag(tag_id, session)
    return deleted_tag
