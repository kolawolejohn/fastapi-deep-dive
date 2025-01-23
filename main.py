from typing import List
from fastapi import FastAPI, HTTPException, status
import uvicorn
from loc_db import books
from models.book_model import Book, BookUpdateModel

app = FastAPI()


@app.get("/books", status_code=200, response_model=List[Book])
async def get_all_books():
    return books


@app.post("/books", status_code=status.HTTP_201_CREATED)
async def create_book(data: Book) -> dict:
    new_book = data.model_dump()
    books.append(new_book)
    return new_book


@app.get("/books/{id}", status_code=status.HTTP_200_OK)
async def get_book(id: int) -> dict:
    for book in books:
        if book["id"] == id:
            return book
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Record not found"
    )


@app.patch("/books/{id}", status_code=status.HTTP_200_OK)
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


@app.delete("/books/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(id: int):
    for book in books:
        if book["id"] == id:
            books.remove(book)
            return
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Record not found"
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
