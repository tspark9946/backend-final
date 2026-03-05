from enum import IntEnum

from pydantic import ConfigDict
from sqlalchemy.dialects.mysql import TINYINT
from sqlmodel import Column, Field, SQLModel, text


class ContactType(IntEnum):
    TEL = 0
    MOBILE = 1
    EMAIL = 2


class TelBase(SQLModel):
    tel_number: str = Field(max_length=32, nullable=True)
    tel_name: str = Field(max_length=64, nullable=True)
    tel_default: bool = Field(default=None, nullable=True)
    tel_type: int | None = Field(
        default=0, sa_column=Column(TINYINT, nullable=False, server_default=text("0"))
    )
    tel_allow_phone: bool = Field(
        default=False, sa_column=Column(TINYINT, nullable=False, server_default=text("0"))
    )
    tel_allow_sms: bool = Field(
        default=False, sa_column=Column(TINYINT, nullable=False, server_default=text("0"))
    )
    tel_allow_email: bool = Field(
        default=False, sa_column=Column(TINYINT, nullable=False, server_default=text("0"))
    )
    created_sign_name: str = Field(default=None, max_length=32)
    modified_sign_name: str = Field(default=None, max_length=32)

    model_config = ConfigDict(from_attributes=True)
