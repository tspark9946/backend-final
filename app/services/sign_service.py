from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.models import Sign
from app.schemas.sign import SignCreate
from app.utils.hashing import Hash


class SignService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_user_by_email(self, email: str):
        statement = select(Sign).where(Sign.sign_email == email)
        result = await self._session.exec(statement)
        user = result.first()

        return user

    async def user_exists(self, email: str) -> bool:
        user = await self.get_user_by_email(email)
        return True if user is not None else False

    async def create_user(self, user_data: SignCreate) -> Sign:
        user_data_dict = user_data.model_dump()

        new_user = Sign(**user_data_dict)

        new_user.sign_password = Hash.bcrypt(user_data_dict["sign_password"])
        # new_user.role = "user"

        self._session.add(new_user)

        await self._session.commit()
        await self._session.refresh(new_user)

        return new_user

    async def get_sign(self, sign_id: int) -> Sign | None:
        statement = select(Sign).where(Sign.sign_id == sign_id)
        results = await self._session.exec(statement)
        return results.first()

    async def get_signs(self, skip: int = 0, limit: int = 100) -> list[Sign]:
        statement = select(Sign).offset(skip).limit(limit)
        results = await self._session.exec(statement)
        return results.scalars().all()
