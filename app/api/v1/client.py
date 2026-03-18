from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.database import get_session
from app.errors import ClientNotFound, TelNotFound
from app.schemas.client import ClientCreate, ClientResponse, ClientUpdate, TelCreate, TelResponse, TelUpdate
from app.services.client_service import ClientService
from app.utils.dependencies import (
    AccessTokenBearer,
    RoleChecker,
)

router = APIRouter(
    prefix="/client",
    tags=["client"],
    # dependencies=[
    #     Depends(AccessTokenBearer()),
    #     Depends(RoleChecker(allowed_roles=["admin", "user"])),
    # ],
)

client_service = ClientService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(allowed_roles=["admin", "user"]))


@router.post(
    "/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED, dependencies=[role_checker]
)
async def create_client(
    client_data: ClientCreate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    # 1. 토큰에서 유저 정보 추출
    sign_info = token_details["user"]

    # 2. Pydantic 모델의 데이터를 업데이트 (Python 3.12 스타일)
    # 직접 할당 방식보다 model_copy가 유효성 검사 측면에서 안전합니다.
    update_data = {
        "created_sign_id": sign_info["sign_id"],
        "created_sign_name": sign_info["sign_name"],
        "hospital_id": sign_info["hospital_id"],
    }

    # 기존 데이터에 유저 정보를 병합
    client_with_auth = client_data.model_copy(update=update_data)
    new_client = await client_service.create_client_with_tels(session=session, client_in=client_with_auth)
    return new_client


@router.get("/", response_model=list[ClientResponse], dependencies=[role_checker])
async def read_all_client(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
    skip: int = 0,
    limit: int = 100,
):
    sign_info = token_details["user"]
    hospital_id = sign_info["hospital_id"]
    clients = await client_service.get_clients(
        session=session, hospital_id=hospital_id, skip=skip, limit=limit
    )
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
    update_data = {
        "updated_sign_id": sign_info["sign_id"],
        "updated_sign_name": sign_info["sign_name"],
        "hospital_id": sign_info["hospital_id"],
    }

    client_data_with_auth = client_data.model_copy(update=update_data)
    dump_data = client_data_with_auth.model_dump(exclude_none=True)
    updated_client = await client_service.update_client_with_tels(
        session=session, client_id=client_id, client_data_dict=dump_data
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


@router.post("/{client_id}/tel", status_code=status.HTTP_201_CREATED, dependencies=[role_checker])
async def create_tel(
    client_id: int,
    tel_data: TelCreate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    sign_info = token_details["user"]
    update_data = {
        "created_sign_id": sign_info["sign_id"],
        "created_sign_name": sign_info["sign_name"],
        "hospital_id": sign_info["hospital_id"],
        "client_id": client_id,
    }

    tel_data_with_auth = tel_data.model_copy(update=update_data)
    dump_data = tel_data_with_auth.model_dump(exclude_none=True)
    new_tel = await client_service.create_tel(session=session, tel_data=dump_data)
    return new_tel


@router.put("/{client_id}/tel/{tel_id}", response_model=TelResponse, dependencies=[role_checker])
async def update_tel(
    client_id: int,
    tel_id: int,
    tel_data: TelUpdate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    sign_info = token_details["user"]
    update_data = {
        "updated_sign_id": sign_info["sign_id"],
        "updated_sign_name": sign_info["sign_name"],
        "tel_id": tel_id,
        "client_id": client_id,
    }

    tel_data_with_auth = tel_data.model_copy(update=update_data)

    dump_data = tel_data_with_auth.model_dump(exclude_none=True)
    updated_tel = await client_service.update_tel(session=session, tel_id=tel_id, tel_data=dump_data)
    return updated_tel


@router.delete("/{client_id}/tel/", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker])
async def delete_tel_with_client_id(
    client_id: int,
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(access_token_bearer),
):
    deleted = await client_service.delete_tel_with_client_id(session=session, client_id=client_id)

    if not deleted:
        raise TelNotFound()
    else:
        return {}


@router.delete(
    "/{client_id}/tel/{tel_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker]
)
async def delete_tel(
    client_id: int,
    tel_id: int,
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(access_token_bearer),
):
    deleted = await client_service.delete_tel(session=session, tel_id=tel_id)

    if not deleted:
        raise TelNotFound()
    else:
        return {}


@router.get("/{client_id}/tel/{tel_id}", response_model=TelResponse)
async def read_tel(client_id: int, tel_id: int, session: AsyncSession = Depends(get_session)):
    tel = await client_service.get_tel(session=session, tel_id=tel_id)
    if not tel:
        raise TelNotFound()

    return tel


@router.get("/{client_id}/tel/", response_model=list[TelResponse])
async def read_tels(client_id: int, session: AsyncSession = Depends(get_session)):
    tels = await client_service.get_tels(session=session, client_id=client_id)
    return tels
