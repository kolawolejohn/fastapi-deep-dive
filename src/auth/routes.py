from datetime import datetime, timedelta
import ssl
import certifi
from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.responses import JSONResponse

from src.auth.dependencies import (
    AccessTokenBearer,
    RefreshTokenBearer,
    get_role_checker,
)
from src.db.models import User
from src.auth.schemas import (
    EmailModel,
    LoginResponseModel,
    PasswordResetConfirmModel,
    PasswordResetRequestModel,
    RegisterUserResponseModel,
    UserBooksModel,
    UserCreateModel,
    UserLoginModel,
)
from src.auth.service import UserService, get_user_service
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.utils import (
    create_access_token,
    create_url_safe_token,
    decode_url_safe_token,
    generate_password_hash,
    verify_password,
)
from src.config import Config
from src.db.redis import add_jti_to_blocklist
from src.auth.dependencies import get_current_user
from src.errors import (
    InvalidCredentials,
    InvalidToken,
    PasswordNotMatch,
    UserAlreadyExists,
    UserNotFound,
)

from src.celery_tasks import send_email


auth_router = APIRouter()
context = ssl.create_default_context(cafile=certifi.where())


@auth_router.post("/send_mail")
async def send_mail(emails: EmailModel):
    emails = emails.addresses
    html = "<h1>Welcome to the bookly app, pleased to meet you<h1>"
    subject = "Welcome to the bookly app,"
    send_email.delay(emails, subject, html)
    return {"message": "Email Sent Successfully"}


@auth_router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterUserResponseModel,
)
async def create_user_account(
    data: UserCreateModel,
    bg_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
):
    if await user_service.user_exists(data.email, session):
        raise UserAlreadyExists()

    new_user = await user_service.create_user(data, session)

    token = create_url_safe_token({"email": data.email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"
    html_message = f"""
    <h2>Verify your email address</h2>
    <p>Please click this<a href="{link}">link </a> to verify your email</p>
    """
    subject = "Verify Email"
    send_email.delay([data.email], subject, html_message)

    return {
        "message": "Account created, please check email to verify your email",
        "user": new_user,
    }


@auth_router.get("/verify/{token}")
async def verify_token(
    token: str,
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
):
    token_data = decode_url_safe_token(token)
    user_mail = token_data.get("email")

    if user_mail:
        user = await user_service.get_user_by_email(user_mail, session)

        if not user:
            raise UserNotFound()
        await user_service.update_user(user, {"is_verified": True}, session)

        return JSONResponse(
            content={"message": "Account verified successfully"},
            status_code=status.HTTP_200_OK,
        )
    return JSONResponse(
        content={"message": "Error occured verifying your account"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


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


@auth_router.post("/password-reset-request")
async def password_reset_request(
    data: PasswordResetRequestModel, bg_tasks: BackgroundTasks
):
    token = create_url_safe_token({"email": data.email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"
    html_message = f"""
    <h2>Reset your password</h2>
    <p>Please click this<a href="{link}">link </a> to reset your password</p>
    """
    subject = "Reset Password"
    send_mail.delay([data.email], subject, html_message)

    return JSONResponse(
        content={
            "message": "Password reset link sent, please check your email to reset your password",
        },
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/password-reset-confirm/{token}")
async def reset_account_password(
    token: str,
    passwords: PasswordResetConfirmModel,
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
):
    if passwords.new_password != passwords.confirm_new_password:
        raise PasswordNotMatch()
    token_data = decode_url_safe_token(token)
    user_mail = token_data.get("email")

    if user_mail:
        user = await user_service.get_user_by_email(user_mail, session)

        if not user:
            raise UserNotFound()

        passwd_hash = generate_password_hash(passwords.new_password)
        await user_service.update_user(user, {"password_hash": passwd_hash}, session)

        return JSONResponse(
            content={"message": "Password reset successfully"},
            status_code=status.HTTP_200_OK,
        )
    return JSONResponse(
        content={"message": "Error resetting your password"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
