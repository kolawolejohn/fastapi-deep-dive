from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from src.auth.schemas import (
    LoginResponseModel,
    UserCreateModel,
    UserLoginModel,
    UserModel,
)
from src.auth.service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.utils import create_access_token, decode_token, verify_password
from src.config import Config

auth_router = APIRouter()
user_service = UserService()


@auth_router.post(
    "/signup", status_code=status.HTTP_201_CREATED, response_model=UserModel
)
async def create_user_account(
    data: UserCreateModel, session: AsyncSession = Depends(get_session)
):
    if await user_service.user_exists(data.email, session):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email {data.email} already exists",
        )
    return await user_service.create_user(data, session)


@auth_router.post(
    "/login", status_code=status.HTTP_200_OK, response_model=LoginResponseModel
)
async def user_login(
    data: UserLoginModel, session: AsyncSession = Depends(get_session)
):
    email, password = data.email, data.password
    user = await user_service.get_user_by_email(email, session)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        data={"email": user.email, "user_id": str(user.id)}
    )
    refresh_token = create_access_token(
        data={"email": user.email, "user_id": str(user.id)},
        refresh=True,
        expiry=timedelta(days=Config.REFRESH_TOKEN_EXPIRY),
    )

    return {
        "message": "Logged in successfully",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "email": user.email,
            "id": str(user.id),
            "username": user.username,
        },
    }
