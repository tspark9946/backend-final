from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.models import Client
from app.schemas.client import ClientCreate


class ClientService:
    async def create_client(self, session: AsyncSession, client_data: ClientCreate) -> Client:
        client = Client(**client_data.model_dump())
        session.add(client)
        await session.commit()
        await session.refresh(client)
        return client

    async def get_client(self, session: AsyncSession, client_id: int) -> Client | None:
        statement = select(Client).where(Client.client_id == client_id)
        results = await session.exec(statement)
        return results.first()

    async def get_clients(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> list[Client]:
        statement = select(Client).offset(skip).limit(limit)
        results = await session.exec(statement)
        return results.all()

    async def update_client(self, session: AsyncSession, client: Client, client_data: dict) -> Client:

        for key, value in client_data.items():
            setattr(client, key, value)

        await session.commit()
        await session.refresh(client)

        return client

    async def delete_client(self, session: AsyncSession, client_id: int) -> bool:
        client = await self.get_client(session=session, client_id=client_id)
        if client is not None:
            await session.delete(client)
            await session.commit()
            return True
        else:
            return False
