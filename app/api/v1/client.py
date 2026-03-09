from typing import List

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.database import get_session
from app.errors import ClientNotFound
from app.schemas.client import ClientCreate, ClientResponse, ClientUpdate
from app.services.client_service import ClientService
from app.utils.dependencies import (
    AccessTokenBearer,
    RoleChecker,
)

router = APIRouter()
client_service = ClientService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(allowed_roles=["admin", "user"]))


@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[role_checker])
async def create_client(
    client_data: ClientCreate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    sign_info = token_details["user"]
    client_data.created_sign_id = sign_info["sign_id"]
    client_data.created_sign_name = sign_info["sign_name"]
    client_data.hospital_id = sign_info["hospital_id"]
    new_client = await client_service.create_client(session=session, client_data=client_data)
    return new_client


@router.get("/all", response_model=List[ClientResponse], dependencies=[role_checker])
async def read_all_client(
    session: AsyncSession = Depends(get_session), _: bool = Depends(access_token_bearer)
):
    clients = await client_service.get_clients(session=session)
    return clients


@router.get("/{client_id}", response_model=ClientResponse)
async def read_client(client_id: int, session: AsyncSession = Depends(get_session)):
    client = await client_service.get_client(session=session, client_id=client_id)
    if not client:
        raise ClientNotFound()
    return client


@router.put("/{client_id}", response_model=ClientResponse, dependencies=[role_checker])
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    sign_info = token_details["user"]
    client_data.created_sign_name = sign_info["sign_name"]
    client_data.hospital_id = sign_info["hospital_id"]

    client = await client_service.get_client(session=session, client_id=client_id)
    if not client:
        raise ClientNotFound()

    updated_client = await client_service.update_client(
        session=session, client=client, client_data=client_data.model_dump(exclude_none=True)
    )
    return updated_client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker])
async def delete_client(
    client_id: int,
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(access_token_bearer),
):
    deleted = await client_service.delete_client(session=session, client_id=client_id)

    if not deleted:
        raise ClientNotFound()
    else:
        return {}
