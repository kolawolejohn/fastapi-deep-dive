from datetime import datetime
from typing import List
import uuid
from pydantic import BaseModel, Field

from src.books.schemas import Book
from src.reviews.schemas import ReviewModel


class UserCreateModel(BaseModel):
    username: str = Field(..., json_schema_extra={"maxlength": 15})
    email: str = Field(..., json_schema_extra={"maxlength": 100})
    first_name: str
    last_name: str
    password: str = Field(..., json_schema_extra={"minlength": 6})


class UserModel(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_verified: bool
    password_hash: str = Field(exclude=True)
    created_at: datetime
    updated_at: datetime


class UserBooksModel(UserModel):
    books: List[Book]
    reviews: List[ReviewModel]


class UserLoginModel(BaseModel):
    email: str = Field(..., json_schema_extra={"maxlength": 100})
    password: str = Field(..., json_schema_extra={"minlength": 6})


class UserDetail(BaseModel):
    email: str
    id: str


class LoginResponseModel(BaseModel):
    message: str
    access_token: str
    refresh_token: str
    user: UserDetail


class EmailModel(BaseModel):
    addresses: List[str]


class RegisterUserResponseModel(BaseModel):
    message: str
    user: UserModel


class PasswordResetRequestModel(BaseModel):
    email: str


class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str
