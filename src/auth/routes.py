from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from src.auth.dependencies import (
    AccessTokenBearer,
    RefreshTokenBearer,
    get_role_checker,
)
from src.db.models import User
from src.auth.schemas import (
    LoginResponseModel,
    UserBooksModel,
    UserCreateModel,
    UserLoginModel,
    UserModel,
)
from src.auth.service import UserService, get_user_service
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.utils import create_access_token, verify_password
from src.config import Config
from src.db.redis import add_jti_to_blocklist
from src.auth.dependencies import get_current_user, RoleChecker
from src.errors import InvalidCredentials, InvalidToken, UserAlreadyExists

auth_router = APIRouter()


@auth_router.post(
    "/signup", status_code=status.HTTP_201_CREATED, response_model=UserModel
)
async def create_user_account(
    data: UserCreateModel,
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
):
    if await user_service.user_exists(data.email, session):
        raise UserAlreadyExists()
    return await user_service.create_user(data, session)


@auth_router.post(
    "/login", status_code=status.HTTP_200_OK, response_model=LoginResponseModel
)
async def user_login(
    data: UserLoginModel,
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
):
    email, password = data.email, data.password
    user = await user_service.get_user_by_email(email, session)
    if not user or not verify_password(password, user.password_hash):
        raise InvalidCredentials()

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
    if token_details["exp"] > datetime.now().timestamp():
        new_access_token = create_access_token(data=token_details["user"])
        return JSONResponse(content={"access_token": new_access_token})

    raise InvalidToken()


@auth_router.get("/me", response_model=UserBooksModel)
async def get_current_user(
    user: User = Depends(get_current_user),
    _: bool = Depends(get_role_checker),
):
    return user


@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details["jti"]

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={"message": "Logged out Successfully"}, status_code=status.HTTP_200_OK
    )
