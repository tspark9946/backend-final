from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.config import settings
from app.db.database import get_session
from app.db.redis import add_jti_to_blocklist
from app.errors import InvalidCredentials, InvalidToken, UserAlreadyExists, UserNotFound
from app.schemas.sign import SignCreate, SignResponse, UserLogin, UserToken
from app.services.sign_service import SignService
from app.utils.dependencies import (
    AccessTokenBearer,
    RefreshTokenBearer,
    RoleChecker,
    get_current_user,
)
from app.utils.hashing import Hash
from app.utils.mail import create_message, mail
from app.utils.token import create_access_token, create_url_safe_token, decode_url_safe_token

router = APIRouter()
role_checker = RoleChecker(allowed_roles=["admin", "user"])


REFRESH_TOKEN_EXPIRY = 2


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_Account(user_data: SignCreate, session: AsyncSession = Depends(get_session)):
    email = user_data.sign_email
    exists = await SignService(session=session).user_exists(email=email)

    if exists:
        raise UserAlreadyExists()

    new_user = await SignService(session=session).create_user(user_data=user_data)

    token = create_url_safe_token({"email": email})

    link = f"http://{settings.DOMAIN}/api/v1/auth/verify/{token}"

    html = f"""
    <h1>Verify your Email</h1>
    <p>Please click this <a href="{link}">link</a> to verify your email</p>
    """

    emails = [email]

    subject = "Verify Your email"
    message = create_message(subject=subject, recipients=emails, body=html)

    await mail.send_message(message)
    print(f"Verification link for {emails}: {html}, {subject}")

    return {
        "message": "Account Created! Check email to verify your account",
        "user": new_user,
    }


@router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):

    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await SignService(session=session).get_user_by_email(email=user_email)

        if not user:
            raise UserNotFound()

        await SignService(session=session).update_user(user, {"is_verified": True})

        return JSONResponse(
            content={"message": "Account verified successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during verification"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@router.post("/login")
async def login_user(user_data: UserLogin, session: AsyncSession = Depends(get_session)):
    email = user_data.sign_email
    password = user_data.sign_password

    user = await SignService(session=session).get_user_by_email(email=email)

    if user is not None:
        password_valid = Hash.verify(plain_password=password, hashed_password=user.sign_password)

        if password_valid:
            access_token = create_access_token(user_data=UserToken.model_validate(user).model_dump())
            # token_data = {
            #     "sign_id": user.sign_id,
            #     "sign_name": user.sign_name,
            #     "sign_email": user.sign_email,
            #     "hospital_id": user.hospital_id,
            # }

            refresh_token = create_access_token(
                user_data=UserToken.model_validate(user).model_dump(),
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
            )

            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {"email": user.sign_email, "uid": str(user.sign_id)},
                }
            )

    raise InvalidCredentials()


@router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])

        return JSONResponse(content={"access_token": new_access_token})

    raise InvalidToken()


@router.get("/me", response_model=SignResponse)
async def get_current_user(user=Depends(get_current_user), _: bool = Depends(role_checker)):
    return user


@router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details["jti"]

    await add_jti_to_blocklist(jti)

    return JSONResponse(content={"message": "Logged Out Successfully"}, status_code=status.HTTP_200_OK)


@router.get("/users/{user_id}", response_model=SignResponse)
async def read_user(user_id: int, session: AsyncSession = Depends(get_session)):
    pass
