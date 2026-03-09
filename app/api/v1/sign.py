from typing import List

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.database import get_session
from app.errors import UserNotFound
from app.schemas.sign import SignResponse, SignUpdate
from app.services.sign_service import SignService
from app.utils.dependencies import (
    AccessTokenBearer,
    RoleChecker,
)

router = APIRouter()
sign_service = SignService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(allowed_roles=["admin", "user"]))


REFRESH_TOKEN_EXPIRY = 2


@router.get("/", response_model=List[SignResponse], dependencies=[role_checker])
async def read_all_user(session: AsyncSession = Depends(get_session), _: bool = Depends(access_token_bearer)):
    users = await sign_service.get_signs(session=session)
    return users


@router.get("/all", response_model=List[SignResponse])
async def read_all_user_none(session: AsyncSession = Depends(get_session)):
    users = await sign_service.get_signs(session=session)
    return users


@router.get("/{user_id}", response_model=SignResponse)
async def read_user(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await sign_service.get_sign(session=session, sign_id=user_id)
    if not user:
        raise UserNotFound()
    return user


@router.put("/{user_id}", response_model=SignResponse, dependencies=[role_checker])
async def update_user(
    user_id: int,
    user_data: SignUpdate,
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(access_token_bearer),
):
    user = await sign_service.get_sign(session=session, sign_id=user_id)
    if not user:
        raise UserNotFound()

    updated_user = await sign_service.update_user(
        session=session, user=user, user_data=user_data.model_dump(exclude_none=True)
    )
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker])
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(access_token_bearer),
):
    deleted = await sign_service.delete_sign(session, user_id)

    if not deleted:
        raise UserNotFound()
    else:
        return {}
