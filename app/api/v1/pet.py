from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.database import get_session
from app.errors import PetNotFound
from app.schemas.pet import PetCreate, PetResponse, PetUpdate
from app.services.pet_service import PetService
from app.utils.dependencies import (
    AccessTokenBearer,
    RoleChecker,
)

router = APIRouter(
    prefix="/client",
    tags=["pet"],
    # dependencies=[
    #     Depends(AccessTokenBearer()),
    #     Depends(RoleChecker(allowed_roles=["admin", "user"])),
    # ],
)

pet_service = PetService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(allowed_roles=["admin", "user"]))


@router.post(
    "/{client_id}/pet/",
    response_model=PetResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[role_checker],
)
async def create_pet(
    client_id: int,
    pet_data: PetCreate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    # 1. 토큰에서 유저 정보 추출
    sign_info = token_details["user"]

    # 2. Pydantic 모델의 데이터를 업데이트 (Python 3.12 스타일)
    # 직접 할당 방식보다 model_copy가 유효성 검사 측면에서 안전합니다.
    update_data = {
        "client_id": client_id,
        "created_sign_id": sign_info["sign_id"],
        "created_sign_name": sign_info["sign_name"],
        "hospital_id": sign_info["hospital_id"],
    }

    # 기존 데이터에 유저 정보를 병합
    pet_with_auth = pet_data.model_copy(update=update_data)
    new_pet = await pet_service.create_pet(session=session, pet_data=pet_with_auth)
    return new_pet


@router.get("/{client_id}/pet/", response_model=list[PetResponse], dependencies=[role_checker])
async def read_pets(
    client_id: int,
    hospital_id: int = Query(default=0, description="병원 ID로 필터링"),
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(access_token_bearer),
):
    if hospital_id:
        pets = await pet_service.get_all_pets(session=session, hospital_id=hospital_id)
    else:
        pets = await pet_service.get_pets(session=session, client_id=client_id)
    return pets


@router.get("/{client_id}/pet/{pet_id}", response_model=PetResponse, dependencies=[role_checker])
async def read_pet(
    client_id: int,
    pet_id: int,
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(access_token_bearer),
):
    pet = await pet_service.get_pet(session=session, client_id=client_id, pet_id=pet_id)
    if pet is None:
        raise PetNotFound
    return pet


@router.delete("/{client_id}/pet/", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker])
async def delete_pet_with_client_id(
    client_id: int,
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(access_token_bearer),
):
    deletedCount = await pet_service.delete_pets_by_client_id(session=session, client_id=client_id)

    if deletedCount:
        return {"detail": f"{deletedCount} pets deleted successfully."}
    else:
        raise PetNotFound()


@router.delete(
    "/{client_id}/pet/{pet_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker]
)
async def delete_pet(
    client_id: int,
    pet_id: int,
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(access_token_bearer),
):
    deleted = await pet_service.delete_pet(session=session, client_id=client_id, pet_id=pet_id)

    if not deleted:
        raise PetNotFound()
    else:
        return {}


@router.put("/{client_id}/pet/{pet_id}", response_model=PetResponse, dependencies=[role_checker])
async def update_pet(
    client_id: int,
    pet_id: int,
    pet_data: PetUpdate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    sign_info = token_details["user"]
    update_data = {
        "client_id": client_id,
        "updated_sign_id": sign_info["sign_id"],
        "updated_sign_name": sign_info["sign_name"],
        "hospital_id": sign_info["hospital_id"],
    }

    pet_data_with_auth = pet_data.model_copy(update=update_data)
    dump_data = pet_data_with_auth.model_dump(exclude_none=True)
    updated_pet = await pet_service.update_pet(
        session=session, client_id=client_id, pet_id=pet_id, pet_data=dump_data
    )
    return updated_pet
