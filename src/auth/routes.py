from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from src.auth.dependencies import AccessTokenBearer, RefreshTokenBearer
from src.auth.models import User
from src.auth.schemas import (
    LoginResponseModel,
    UserBookModel,
    UserCreateModel,
    UserLoginModel,
    UserModel,
)
from src.auth.service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.utils import create_access_token, verify_password
from src.config import Config
from src.db.redis import add_jti_to_blocklist
from src.auth.dependencies import get_current_user, RoleChecker

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin", "user"])


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
        data={"email": user.email, "user_id": str(user.id), "role": user.role}
    )
    refresh_token = create_access_token(
        data={"email": user.email, "user_id": str(user.id), "role": user.role},
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
        },
    }


@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(data=token_details["user"])

        return JSONResponse(content={"access_token": new_access_token})

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired token",
    )


@auth_router.get("/me", response_model=UserBookModel)
async def get_current_user(
    user: User = Depends(get_current_user), _: bool = Depends(role_checker)
):
    return user


@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details["jti"]

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={"message": "Logged out Successfully"}, status_code=status.HTTP_200_OK
    )
