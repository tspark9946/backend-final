from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.database import get_session
from app.errors import VitalNotFound
from app.schemas.common import DateRange
from app.schemas.vital import VitalCreate, VitalResponse, VitalUpdate
from app.services.vital_service import VitalService
from app.utils.dependencies import (
    AccessTokenBearer,
    RoleChecker,
)

router = APIRouter(
    prefix="/pet",
    tags=["pet vital"],
    # dependencies=[
    #     Depends(AccessTokenBearer()),
    #     Depends(RoleChecker(allowed_roles=["admin", "user"])),
    # ],
)

vital_service = VitalService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(allowed_roles=["admin", "user"]))


@router.post(
    "/{pet_id}/vital/",
    response_model=VitalResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[role_checker],
)
async def create_vital(
    pet_id: int,
    vital_data: VitalCreate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    sign_info = token_details["user"]

    update_data = {
        "pet_id": pet_id,
        "created_sign_id": sign_info["sign_id"],
        "created_sign_name": sign_info["sign_name"],
        "hospital_id": sign_info["hospital_id"],
    }

    vital_with_auth = vital_data.model_copy(update=update_data)
    new_vital = await vital_service.create_vital(session=session, vital_data=vital_with_auth)
    return new_vital


@router.get("/{pet_id}/vital/", response_model=list[VitalResponse], dependencies=[role_checker])
async def read_vitals(
    pet_id: int,
    search_date: Annotated[DateRange, Query()],
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(access_token_bearer),
):
    vitals = await vital_service.get_vitals(
        session=session, pet_id=pet_id, start_date=search_date.start_date, end_date=search_date.end_date
    )

    return vitals


@router.get("/{pet_id}/vital/{vital_id}", response_model=VitalResponse, dependencies=[role_checker])
async def read_pet(
    pet_id: int,
    vital_id: int,
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(access_token_bearer),
):
    vital = await vital_service.get_vital(session=session, pet_id=pet_id, vital_id=vital_id)
    if vital is None:
        raise VitalNotFound()
    return vital


@router.delete("/{pet_id}/vital/", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker])
async def delete_vital_with_pet_id(
    pet_id: int,
    search_date: Annotated[DateRange, Query()],
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(access_token_bearer),
):
    deletedCount = await vital_service.delete_vital_by_pet_id(
        session=session, pet_id=pet_id, start_date=search_date.start_date, end_date=search_date.end_date
    )

    if deletedCount:
        return {"detail": f"{deletedCount} pets deleted successfully."}
    else:
        raise VitalNotFound()


@router.delete(
    "/{pet_id}/vital/{vital_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker]
)
async def delete_pet(
    pet_id: int,
    vital_id: int,
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(access_token_bearer),
):
    deleted = await vital_service.delete_vital(session=session, pet_id=pet_id, vital_id=vital_id)

    if not deleted:
        raise VitalNotFound()
    else:
        return {}


@router.put("/{pet_id}/vital/{vital_id}", response_model=VitalResponse, dependencies=[role_checker])
async def update_pet(
    pet_id: int,
    vital_id: int,
    vital_data: VitalUpdate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    sign_info = token_details["user"]
    update_data = {
        "pet_id": pet_id,
        "updated_sign_id": sign_info["sign_id"],
        "updated_sign_name": sign_info["sign_name"],
        "hospital_id": sign_info["hospital_id"],
    }

    vital_data_with_auth = vital_data.model_copy(update=update_data)
    dump_data = vital_data_with_auth.model_dump(exclude_none=True)
    updated_vital = await vital_service.update_vital(
        session=session, pet_id=pet_id, vital_id=vital_id, vital_data=dump_data
    )
    return updated_vital
