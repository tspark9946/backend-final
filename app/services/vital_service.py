from datetime import date

from sqlmodel import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.models import Vital
from app.errors import VitalNotFound
from app.schemas.vital import VitalCreate


class VitalService:
    async def create_vital(self, session: AsyncSession, vital_data: VitalCreate) -> Vital:
        vital = Vital(**vital_data.model_dump())
        session.add(vital)

        await session.commit()
        await session.refresh(vital)

        return vital

    async def get_vital(self, session: AsyncSession, pet_id: int, vital_id: int) -> Vital | None:
        statement = select(Vital).where(Vital.vital_id == vital_id).where(Vital.pet_id == pet_id)
        results = await session.exec(statement)
        return results.first()

    async def get_vitals(
        self, session: AsyncSession, pet_id: int, start_date: date | None = None, end_date: date | None = None
    ) -> list[Vital]:
        statement = select(Vital).where(Vital.pet_id == pet_id)

        if start_date and end_date:
            statement = statement.where(Vital.vital_date.between(start_date, end_date))

        statement = statement.order_by(Vital.vital_date.desc())

        results = await session.exec(statement)
        return results.all()

    async def update_vital(
        self, session: AsyncSession, pet_id: int, vital_id: int, vital_data: dict
    ) -> Vital:
        vital = await self.get_vital(session=session, pet_id=pet_id, vital_id=vital_id)
        if not vital:
            raise VitalNotFound()

        for key, value in vital_data.items():
            setattr(vital, key, value)

        await session.commit()
        await session.refresh(vital)

        return vital

    async def delete_vital(self, session: AsyncSession, pet_id: int, vital_id: int) -> bool:
        vital = await self.get_vital(session=session, pet_id=pet_id, vital_id=vital_id)
        if vital is not None:
            await session.delete(vital)
            await session.commit()
            return True
        else:
            return False

    async def delete_vital_by_pet_id(
        self, session: AsyncSession, pet_id: int, start_date: date | None = None, end_date: date | None = None
    ) -> int:
        statement = delete(Vital).where(Vital.pet_id == pet_id)
        if start_date and end_date:
            statement = statement.where(Vital.vital_date.between(start_date, end_date))

        result = await session.exec(statement)

        await session.commit()

        return result.rowcount
