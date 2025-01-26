import logging
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.dependencies import get_current_user
from src.db.main import get_session
from src.db.models import Review, User
from src.reviews.schemas import ReviewCreateModel
from src.reviews.service import ReviewService, get_review_service

logger = logging.getLogger(__name__)

review_router = APIRouter()


@review_router.post("/book/{book_id}", status_code=status.HTTP_201_CREATED)
async def add_review_to_book(
    book_id: str,
    review_data: ReviewCreateModel,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    review_service: ReviewService = Depends(get_review_service),
) -> Review:
    try:
        new_review = await review_service.add_review_to_book(
            user_email=current_user.email,
            book_id=book_id,
            review_data=review_data,
            session=session,
        )
        return new_review

    except HTTPException as e:
        logger.error("HTTPException occurred: %s", e.detail)
        raise e

    except Exception as e:
        logger.exception("Unexpected error occurred: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
