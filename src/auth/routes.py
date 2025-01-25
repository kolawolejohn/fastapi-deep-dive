from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.schemas import UserCreateModel, UserModel
from src.auth.service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession

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
