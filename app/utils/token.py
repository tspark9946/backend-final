import logging
import uuid
from datetime import datetime, timedelta

import jwt
from itsdangerous import URLSafeTimedSerializer

from app.common.config import settings

ACCESS_TOKEN_EXPIRE = 3600  # 1 hour in seconds


def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False) -> str:
    payload = {}
    payload["user"] = user_data
    payload["exp"] = datetime.now() + (
        expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRE)
    )
    payload["jti"] = str(uuid.uuid4())  # Unique identifier for the token
    payload["refresh"] = refresh  # Indicate if this is a refresh token

    encoded_jwt = jwt.encode(payload=payload, key=settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(jwt=token, key=settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

        return token_data

    except jwt.PyJWTError as e:
        logging.exception(e)
        return None


serializer = URLSafeTimedSerializer(secret_key=settings.JWT_SECRET, salt="email-configuration")


def create_url_safe_token(data: dict):

    token = serializer.dumps(data)

    return token


def decode_url_safe_token(token: str):
    try:
        token_data = serializer.loads(token)

        return token_data

    except Exception as e:
        logging.error(str(e))


# def verify_token(token: str, credentials_exception):
#     try:
#         payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
#         email: str = payload.get("sub")
#         if email is None:
#             raise credentials_exception
#         token_data = schemas.TokenData(email=email)
#     except JWTError:
#         raise credentials_exception
