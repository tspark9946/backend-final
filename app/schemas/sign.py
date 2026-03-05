from datetime import datetime

from pydantic import ConfigDict
from sqlalchemy.dialects.mysql import TINYINT
from sqlmodel import Column, Field, SQLModel, String, text


class SignBase(SQLModel):
    sign_name: str = Field(max_length=32)
    sign_email: str = Field(sa_column=Column(String(64), nullable=False, unique=True, index=True))
    sign_password: str = Field(max_length=255)
    sign_cellphone: str = Field(max_length=50, nullable=True, unique=True)
    sign_license_number: str | None = Field(default=None, max_length=100, nullable=True)
    sign_department: str | None = Field(default=None, max_length=100, nullable=True)
    sign_jobtitle: str | None = Field(default=None, max_length=100, nullable=True)
    sign_resign: int | None = Field(
        default=0,
        sa_column=Column(TINYINT, nullable=False, server_default=text("0")),
    )
    sign_resign_date: datetime | None = Field(default=None, nullable=True)

    model_config = ConfigDict(from_attributes=True)


class SignCreate(SignBase):
    hospital_id: int
    order_idx: int | None = Field(default=None)

    model_config = {
        "json_schema_extra": {
            "example": {
                "sign_name": "John",
                "sign_password": "strongpassword123",
                "sign_email": "johndoe123@co.com",
                "sign_cellphone": "010-1234-5678",
                "sign_license_number": "1234567890",
                "sign_department": "Cardiology",
                "sign_jobtitle": "Cardiologist",
                "hospital_id": 1,
            }
        }
    }


class SignResponse(SignBase):
    sign_id: int
    sign_password: str = Field(exclude=True)
    hospital_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.strftime("%Y-%m-%d %H:%M")},
    )


class SignUpdate(SignBase):
    sign_id: int
    sign_password: str = Field(exclude=True, min_length=8, max_length=255)


class SignDelete(SQLModel):
    sign_id: int


class UserLogin(SQLModel):
    sign_email: str = Field(max_length=64)
    sign_password: str = Field(min_length=6, max_length=255)


class UserToken(SQLModel):
    sign_id: int
    sign_name: str
    sign_email: str
    hospital_id: int

    model_config = ConfigDict(from_attributes=True)


class PasswordResetRequestModel(SQLModel):
    email: str


class PasswordResetConfirmModel(SQLModel):
    new_password: str
    confirm_new_password: str
