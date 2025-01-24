from fastapi import APIRouter, HTTPException, status
from typing import List
from src.books.book_data import books
from src.books.schemas import Book, BookUpdateModel

book_router = APIRouter()


@book_router.get("/", status_code=200, response_model=List[Book])
async def get_all_books():
    return books


@book_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_book(data: Book) -> dict:
    new_book = data.model_dump()
    books.book_routerend(new_book)
    return new_book


@book_router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_book(id: int) -> dict:
    for book in books:
        if book["id"] == id:
            return book
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Record not found"
    )


@book_router.patch("/{id}", status_code=status.HTTP_200_OK)
async def update_book(id: int, data: BookUpdateModel) -> dict:
    for book in books:
        if book["id"] == id:
            book["title"] = data.title
            book["publisher"] = data.publisher
            book["page_count"] = data.page_count
            return book
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Record not found"
    )


@book_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(id: int):
    for book in books:
        if book["id"] == id:
            books.remove(book)
            return
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Record not found"
    )
