import logging
from typing import List
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import Review
from src.auth.service import UserService
from src.books.service import BookService
from src.reviews.schemas import ReviewCreateModel

logger = logging.getLogger(__name__)


class ReviewService:
    def __init__(self, book_service: BookService, user_service: UserService):
        self.book_service = book_service
        self.user_service = user_service

    async def add_review_to_book(
        self,
        user_email: str,
        book_id: str,
        review_data: ReviewCreateModel,
        session: AsyncSession,
    ) -> Review:
        try:

            book = await self.book_service.get_book(id=book_id, session=session)
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Book not found",
                )

            user = await self.user_service.get_user_by_email(
                email=user_email, session=session
            )
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            existing_review = (
                await session.exec(
                    select(Review).where(
                        Review.user_id == user.id, Review.book_id == book.id
                    )
                )
            ).first()

            if existing_review:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You have already reviewed this book",
                )

            review_data_dict = review_data.model_dump()
            new_review = Review(**review_data_dict, user=user, book=book)

            session.add(new_review)
            await session.commit()
            await session.refresh(new_review)

            return new_review

        except HTTPException:
            raise  # Re-raise HTTPException to propagate it
        except Exception as e:
            logger.exception("Failed to add review to book: %s", e)
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    async def get_reviews_by_user(
        self,
        user_id: str,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 10,
    ) -> List[Review]:
        try:
            reviews = (
                await session.exec(
                    select(Review)
                    .where(Review.user_id == user_id)
                    .offset(skip)
                    .limit(limit)
                )
            ).all()
            return reviews
        except Exception as e:
            logger.exception("Failed to fetch reviews by user: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    async def get_review_by_id(
        self,
        id: str,
        session: AsyncSession,
    ) -> Review:
        try:
            review = await session.get(Review, id)
            if not review:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Review not found",
                )
            return review
        except Exception as e:
            logger.exception("Failed to fetch review by ID: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    async def update_review(
        self,
        id: str,
        user_id: str,
        review_data: ReviewCreateModel,
        session: AsyncSession,
    ) -> Review:
        review = await session.get(Review, id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found",
            )
        if review.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to update this review",
            )

        if review_data.rating is not None:
            review.rating = review_data.rating
        if review_data.review_text is not None:
            review.review_text = review_data.review_text

        session.add(review)
        await session.commit()
        await session.refresh(review)

        return review

    async def delete_review(
        self,
        id: str,
        user_id: str,
        session: AsyncSession,
    ):
        review = await session.get(Review, id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found",
            )
        if review.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to delete this review",
            )

        await session.delete(review)
        await session.commit()


def get_review_service(
    book_service: BookService = Depends(BookService),
    user_service: UserService = Depends(UserService),
) -> ReviewService:
    return ReviewService(book_service, user_service)
