from fastapi import FastAPI
import uvicorn
from src.books.routes import book_router

version = "v1"

app = FastAPI(
    version=version, title="Bookly", description="Rest Api for a book review service"
)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])


# run the code with:  fastapi dev src/
