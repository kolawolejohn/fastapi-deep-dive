from fastapi import FastAPI
from src.books.routes import book_router
from src.auth.routes import auth_router
from src.reviews.routes import review_router
from src.tags.routes import tags_router
from .errors import register_error_handlers
from .middleware import register_middleware


version = "v1"

app = FastAPI(
    version=version,
    title="Bookly",
    description="Rest Api for a book review service",
    docs_url=f"/api/{version}/docs",
    redoc_url=f"/api/{version}/redoc",
    contact={
        "name": "Kolawole Ogunfowokan",
        "email": "kolawole.oajohn@gmail.com",
        "url": "https://github.com/kolawolejohn/fastapi-deep-dive",
    },
    openapi_url=f"/api/{version}/openapi.json",
)

register_error_handlers(app)
register_middleware(app)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])
app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=["reviews"])
app.include_router(tags_router, prefix=f"/api/{version}/tags", tags=["tags"])


# run the code with:  fastapi dev src/
