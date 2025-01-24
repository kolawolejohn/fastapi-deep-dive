from fastapi import FastAPI
from src.books.routes import book_router
from contextlib import asynccontextmanager
from src.db.main import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server is starting....")
    await init_db()
    yield
    print("Server has been stopped")


version = "v1"

app = FastAPI(
    version=version,
    title="Bookly",
    description="Rest Api for a book review service",
    lifespan=lifespan,
)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])


# run the code with:  fastapi dev src/
