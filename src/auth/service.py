from fastapi import HTTPException, status
from sqlmodel import select

from src.auth.schemas import UserCreateModel, UserLoginModel
from src.auth.utils import generate_password_hash
from src.db.models import User
from sqlmodel.ext.asyncio.session import AsyncSession


class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)

        result = await session.exec(statement)

        user = result.first()

        return user

    async def user_exists(self, email: str, session: AsyncSession):
        user = await self.get_user_by_email(email, session)

        return user is not None

    async def create_user(self, data: UserCreateModel, session: AsyncSession):
        data_dict = data.model_dump()
        new_user = User(**data_dict)
        # new_user.password_hash = generate_password_hash(data_dict["password"])
        new_user = {
            "password_hash": generate_password_hash(data_dict["password"]),
            "role": "user",
        }
        session.add(new_user)
        await session.commit()
        return new_user

    async def user_login(self, data: UserLoginModel, session: AsyncSession):
        pass


async def get_user_service():
    return UserService()
