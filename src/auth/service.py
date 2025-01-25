from sqlmodel import select

from src.auth.schemas import UserCreateModel
from src.auth.utils import generate_password_hash
from .models import User
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
        new_user.password_hash = generate_password_hash(data_dict["password"])
        session.add(new_user)
        await session.commit()
        return new_user
