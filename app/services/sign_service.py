from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.models import Sign
from app.schemas.sign import SignCreate
from app.utils.hashing import Hash


class SignService:
    async def get_user_by_email(self, session: AsyncSession, email: str):
        statement = select(Sign).where(Sign.sign_email == email)
        result = await session.exec(statement)
        user = result.first()

        return user

    async def user_exists(self, session: AsyncSession, email: str) -> bool:
        user = await self.get_user_by_email(session=session, email=email)
        return True if user is not None else False

    async def create_user(self, session: AsyncSession, user_data: SignCreate) -> Sign:
        user_data_dict = user_data.model_dump()

        new_user = Sign(**user_data_dict)

        new_user.sign_password = Hash.bcrypt(user_data_dict["sign_password"])
        # new_user.role = "user"

        session.add(new_user)

        await session.commit()
        await session.refresh(new_user)

        return new_user

    async def update_user(self, session: AsyncSession, user: Sign, user_data: dict) -> Sign:

        for key, value in user_data.items():
            setattr(user, key, value)

        await session.commit()
        await session.refresh(user)

        return user

    async def get_sign(self, session: AsyncSession, sign_id: int) -> Sign | None:
        statement = select(Sign).where(Sign.sign_id == sign_id)
        results = await session.exec(statement)
        return results.first()

    async def get_signs(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> list[Sign]:
        statement = select(Sign).offset(skip).limit(limit)
        results = await session.exec(statement)
        return results.all()
