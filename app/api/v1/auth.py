from datetime import datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.config import settings
from app.db.database import get_session
from app.db.redis import add_jti_to_blocklist
from app.errors import InvalidCredentials, InvalidToken, UserAlreadyExists, UserNotFound
from app.schemas.sign import (
    PasswordResetConfirmModel,
    PasswordResetRequestModel,
    SignCreate,
    SignResponse,
    UserLogin,
    UserToken,
)
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
sign_service = SignService()
role_checker = RoleChecker(allowed_roles=["admin", "user"])


REFRESH_TOKEN_EXPIRY = 2


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_Account(
    user_data: SignCreate, bg_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)
):
    email = user_data.sign_email
    exists = await sign_service.user_exists(session=session, email=email)

    if exists:
        raise UserAlreadyExists()

    new_user = await sign_service.create_user(session=session, user_data=user_data)

    token = create_url_safe_token({"email": email})

    link = f"http://{settings.DOMAIN}/api/v1/auth/verify/{token}"

    html = f"""
    <h1>Verify your Email</h1>
    <p>Please click this <a href="{link}">link</a> to verify your email</p>
    """

    emails = [email]

    subject = "Verify Your email"
    message = create_message(subject=subject, recipients=emails, body=html)

    # background task로 이메일 전송하여 API 응답 지연 방지
    # 임시 메일 생성때문에 임시로 주석처리
    # bg_tasks.add_task(mail.send_message, message)

    return {
        "message": "Account Created! Check email to verify your account",
        "user": new_user.model_dump(exclude={"sign_password"}),
    }


@router.post("/login")
async def login_user(user_data: UserLogin, session: AsyncSession = Depends(get_session)):
    email = user_data.sign_email
    password = user_data.sign_password

    user = await sign_service.get_user_by_email(session=session, email=email)

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


@router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details["jti"]

    await add_jti_to_blocklist(jti)

    return JSONResponse(content={"message": "Logged Out Successfully"}, status_code=status.HTTP_200_OK)


@router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])

        return JSONResponse(content={"access_token": new_access_token})

    raise InvalidToken(name="Refresh Token Expired", message="Please login again to get new tokens")


@router.get("/me", response_model=SignResponse)
async def get_current_user(user=Depends(get_current_user), _: bool = Depends(role_checker)):
    """
    현재 로그인한 사용자의 정보를 반환하는 엔드포인트입니다. \n
    Access Token을 검증하여 사용자 정보를 추출하고, 해당 정보를 기반으로 데이터베이스에서 사용자를 조회하여 반환합니다.\n
    사용자 정보는 SignResponse 모델로 직렬화되어 반환됩니다."""
    return user


@router.get("/verify/{token}", include_in_schema=False)
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    """
    이메일 인증을 위한 엔드포인트입니다.\n
    사용자가 이메일에 포함된 링크를 클릭하면 이 엔드포인트가 호출됩니다.\n
    URL-safe 토큰을 디코딩하여 이메일을 추출하고, 해당 이메일을 가진 사용자를 데이터베이스에서 조회하여 계정을 활성화합니다.
    """

    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await sign_service.get_user_by_email(session=session, email=user_email)

        if not user:
            raise UserNotFound()

        await sign_service.update_user(session=session, user=user, user_data={"is_verified": True})

        return JSONResponse(
            content={"message": "Account verified successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during verification"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@router.post("/password-reset-request", include_in_schema=False)
async def password_reset_request(email_data: PasswordResetRequestModel, bg_tasks: BackgroundTasks):
    email = email_data.email

    token = create_url_safe_token({"email": email})

    link = f"http://{settings.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"

    html_message = f"""
    <h1>Reset Your Password</h1>
    <p>Please click this <a href="{link}">link</a> to Reset Your Password</p>
    """
    subject = "Reset Your Password"

    emails = [email]

    message = create_message(subject=subject, recipients=emails, body=html_message)

    bg_tasks.add_task(mail.send_message, message)

    return JSONResponse(
        content={
            "message": "Please check your email for instructions to reset your password",
        },
        status_code=status.HTTP_200_OK,
    )


@router.post("/password-reset-confirm/{token}", include_in_schema=False)
async def reset_account_password(
    token: str,
    passwords: PasswordResetConfirmModel,
    session: AsyncSession = Depends(get_session),
):
    new_password = passwords.new_password
    confirm_password = passwords.confirm_new_password

    if new_password != confirm_password:
        raise HTTPException(detail="Passwords do not match", status_code=status.HTTP_400_BAD_REQUEST)

    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await sign_service.get_user_by_email(session, user_email)

        if not user:
            raise UserNotFound()

        passwd_hash = Hash.bcrypt(new_password)
        await sign_service.update_user(session, user, {"sign_password": passwd_hash})

        return JSONResponse(
            content={"message": "Password reset Successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during password reset."},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
