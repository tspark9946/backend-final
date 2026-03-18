from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.models import Pet
from app.errors import PetNotFound
from app.schemas.pet import PetCreate


class PetService:
    async def create_pet(self, session: AsyncSession, pet_data: PetCreate) -> Pet:
        pet = Pet(**pet_data.model_dump())
        session.add(pet)
        await session.commit()
        await session.refresh(pet)
        return pet

    async def get_pets(self, session: AsyncSession, client_id: int) -> list[Pet]:
        statement = select(Pet).where(Pet.client_id == client_id)
        results = await session.exec(statement)
        return results.all()

    async def get_pet(self, session: AsyncSession, client_id: int, pet_id: int) -> Pet | None:
        statement = select(Pet).where(Pet.pet_id == pet_id, Pet.client_id == client_id)
        results = await session.exec(statement)
        return results.first()

    async def get_all_pets(
        self, session: AsyncSession, hospital_id: int, skip: int = 0, limit: int = 100
    ) -> list[Pet]:
        statement = select(Pet).where(Pet.hospital_id == hospital_id).offset(skip).limit(limit)
        results = await session.exec(statement)
        return results.all()

    async def delete_pet(self, session: AsyncSession, client_id: int, pet_id: int) -> bool:
        pet = await self.get_pet(session=session, client_id=client_id, pet_id=pet_id)
        if pet is not None:
            await session.delete(pet)
            await session.commit()
            return True
        else:
            return False

    async def delete_pets_by_client_id(self, session: AsyncSession, client_id: int) -> int:
        # 1. client_id가 일치하는 모든 Tel 레코드를 삭제하는 구문 생성
        statement = delete(Pet).where(Pet.client_id == client_id)

        # 2. 쿼리 실행
        result = await session.exec(statement)

        # 3. 변경 사항 반영
        await session.commit()

        # rowcount를 통해 실제 삭제된 데이터가 있는지 확인 (선택 사항)
        return result.rowcount

    async def update_pet(self, session: AsyncSession, client_id: int, pet_id: int, pet_data: dict) -> Pet:
        pet = await self.get_pet(session=session, client_id=client_id, pet_id=pet_id)
        if not pet:
            raise PetNotFound()

        for key, value in pet_data.items():
            setattr(pet, key, value)

        try:
            await session.commit()
            await session.refresh(pet)
            return pet
        except SQLAlchemyError:
            await session.rollback()
            raise Exception("데이터베이스 오류발생")
