from typing import List

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.database import get_session
from app.errors import UserNotFound
from app.schemas.sign import SignResponse
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


@router.get("/{user_id}", response_model=SignResponse)
async def read_user(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await sign_service.get_sign(session=session, user_id=user_id)
    if not user:
        raise UserNotFound()
    return user
