from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, field_validator


class ReviewModel(BaseModel):
    id: uuid.UUID
    rating: int
    review_text: str
    user_id: uuid.UUID
    book_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ReviewCreateModel(BaseModel):
    rating: Optional[int] = None
    review_text: Optional[str] = None

    @field_validator("rating")
    def validate_rating(cls, value):
        if value < 1 or value > 5:
            raise ValueError("Rating must be between 1 and 5")
        return value
