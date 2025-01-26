import logging
from typing import List
from fastapi import APIRouter, Depends, Query, status
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.dependencies import get_current_user
from src.db.main import get_session
from src.db.models import Review, User
from src.reviews.schemas import ReviewCreateModel, ReviewModel
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


@review_router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=ReviewModel,
    summary="Fetch a review by ID",
    description="Fetch a review by its unique ID.",
    responses={
        200: {"description": "Review fetched successfully"},
        404: {"description": "Review not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_review_by_id(
    id: str,
    session: AsyncSession = Depends(get_session),
    review_service: ReviewService = Depends(get_review_service),
):
    try:
        review = await review_service.get_review_by_id(
            id=id,
            session=session,
        )
        return review
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@review_router.get(
    "/user/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[ReviewModel],
    summary="Fetch all reviews by a user",
    description="Fetch all reviews written by a specific user.",
    responses={
        200: {"description": "Reviews fetched successfully"},
        500: {"description": "Internal server error"},
    },
)
async def get_reviews_by_user(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    session: AsyncSession = Depends(get_session),
    review_service: ReviewService = Depends(get_review_service),
):
    try:
        reviews = await review_service.get_reviews_by_user(
            user_id=user_id,
            session=session,
            skip=skip,
            limit=limit,
        )
        return reviews
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@review_router.patch(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=ReviewModel,
    summary="Update a review",
    description="Update a review by its ID. Only the user who created the review can update it.",
    responses={
        200: {"description": "Review updated successfully"},
        403: {"description": "You are not authorized to update this review"},
        404: {"description": "Review not found"},
        500: {"description": "Internal server error"},
    },
)
async def update_review(
    id: str,
    review_data: ReviewCreateModel,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    review_service: ReviewService = Depends(get_review_service),
) -> Review:
    try:
        updated_review = await review_service.update_review(
            id=id,
            user_id=current_user.id,
            review_data=review_data,
            session=session,
        )
        return updated_review
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@review_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a review",
    description="Delete a review by its ID. Only the user who created the review can delete it.",
    responses={
        204: {},
        403: {"description": "You are not authorized to delete this review"},
        404: {"description": "Review not found"},
        500: {"description": "Internal server error"},
    },
)
async def delete_review(
    id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    review_service: ReviewService = Depends(get_review_service),
):
    is_deleted = await review_service.delete_review(
        id=id, user_id=current_user.id, session=session
    )
    if is_deleted:
        return None
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Record not found"
    )
