## Arjan's code에서 만든 예외등록파일이나 제대로 작동하지 않아 보류
# 참고영상
# https://www.youtube.com/watch?v=7MHDDOrDx-w

from typing import Callable

from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse


class SkyPulseApiError(Exception):
    """base exception class"""

    def __init__(self, message: str = "Service is unavailable", name: str = "SkyPulse"):
        self.message = message
        self.name = name
        super().__init__(self.message, self.name)


class ServiceError(SkyPulseApiError):
    """failures in external services or APIs, like a database or a third-party service"""

    pass


class EntityDoesNotExistError(SkyPulseApiError):
    """database returns nothing"""

    pass


class EntityAlreadyExistsError(SkyPulseApiError):
    """conflict detected, like trying to create a resource that already exists"""

    pass


class InvalidOperationError(SkyPulseApiError):
    """invalid operations like trying to delete a non-existing entity, etc."""

    pass


class AuthenticationFailed(SkyPulseApiError):
    """invalid authentication credentials"""

    pass


class InvalidTokenError(SkyPulseApiError):
    """invalid token"""

    pass


class InvalidCredentials(SkyPulseApiError):
    """User has provided wrong email or password during log in."""

    pass


def create_exception_handler(
    status_code: int, initial_detail: str
) -> Callable[[Request, SkyPulseApiError], JSONResponse]:
    detail = {"message": initial_detail}  # Using a dictionary to hold the detail

    async def exception_handler(_: Request, exc: SkyPulseApiError) -> JSONResponse:
        if exc.message:
            detail["message"] = exc.message

        if exc.name:
            detail["message"] = f"{detail['message']} [{exc.name}]"

        # logger.error(exc)
        return JSONResponse(status_code=status_code, content={"detail": detail["message"]})

    return exception_handler


def register_all_errors2(app: FastAPI):

    app.add_exception_handler(
        exc_class_or_status_code=EntityDoesNotExistError,
        handler=create_exception_handler(status.HTTP_404_NOT_FOUND, "Entity does not exist."),
    )

    app.add_exception_handler(
        exc_class_or_status_code=InvalidOperationError,
        handler=create_exception_handler(status.HTTP_400_BAD_REQUEST, "Can't perform the operation."),
    )

    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(status.HTTP_400_BAD_REQUEST, "Invalid Email Or Password"),
    )

    app.add_exception_handler(
        exc_class_or_status_code=AuthenticationFailed,
        handler=create_exception_handler(
            status.HTTP_401_UNAUTHORIZED,
            "Authentication failed due to invalid credentials.",
        ),
    )

    app.add_exception_handler(
        exc_class_or_status_code=InvalidTokenError,
        handler=create_exception_handler(
            status.HTTP_401_UNAUTHORIZED, "Invalid token, please re-authenticate again."
        ),
    )

    app.add_exception_handler(
        exc_class_or_status_code=ServiceError,
        handler=create_exception_handler(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "A service seems to be down, try again later.",
        ),
    )
