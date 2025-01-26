from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from src.books.schemas import BookCreateModel, BookReviewDetailModel, BookUpdateModel
from src.db.models import Book
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.books.service import BookService
from src.auth.dependencies import AccessTokenBearer, RoleChecker

book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(["admin", "user"]))


@book_router.get(
    "/",
    status_code=200,
    response_model=List[Book],
    dependencies=[role_checker],
)
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    books = await book_service.get_all_books(session)
    return books


@book_router.get(
    "/user/{user_id}",
    status_code=200,
    response_model=List[Book],
    dependencies=[role_checker],
)
async def get_user_book_submission(
    user_id: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    user_id = token_details["user"]["user_id"]
    books = await book_service.get_user_books(user_id, session)
    return books


@book_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Book,
    dependencies=[role_checker],
)
async def create_book(
    data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
) -> dict:
    user_id = token_details["user"]["user_id"]
    new_book = await book_service.create_book(data, user_id, session)
    return new_book


@book_router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=BookReviewDetailModel,
    dependencies=[role_checker],
)
async def get_book(
    id: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
) -> dict:
    book = await book_service.get_book(id, session)

    if book:
        return book
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record not found"
        )


@book_router.patch(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=Book,
    dependencies=[role_checker],
)
async def update_book(
    id: str,
    data: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
) -> dict:
    book = await book_service.update_book(id, data, session)
    if book:
        return book
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record not found"
        )


@book_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[role_checker],
)
async def delete_book(
    id: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    is_deleted = await book_service.delete_book(id, session)
    if is_deleted:
        return None  # 204 No Content response
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Record not found"
    )
