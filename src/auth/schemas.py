from datetime import datetime
from typing import List
import uuid
from pydantic import BaseModel, Field

from src.books.schemas import Book


class UserCreateModel(BaseModel):
    username: str = Field(maxlength=15)
    email: str = Field(max_length=100)
    first_name: str
    last_name: str
    password: str = Field(min_length=6)


class UserModel(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    password_hash: str = Field(exclude=True)
    created_at: datetime
    updated_at: datetime


class UserBookModel(UserModel):
    books: List[Book]


class UserLoginModel(BaseModel):
    email: str = Field(max_length=100)
    password: str = Field(min_length=6)


class UserDetail(BaseModel):
    email: str
    id: str


class LoginResponseModel(BaseModel):
    message: str
    access_token: str
    refresh_token: str
    user: UserDetail
