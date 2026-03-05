from datetime import date

from pydantic import ConfigDict
from sqlalchemy.dialects.mysql import TINYINT
from sqlmodel import Boolean, Column, Date, Field, SQLModel, Text, text


class PetBase(SQLModel):
    pet_serial: int = Field(nullable=False, index=True)
    pet_name: str = Field(max_length=64, nullable=True)
    pet_rfid: str = Field(max_length=64, nullable=True)
    pet_rfidtype: int = Field(
        default=0,
        sa_column=Column(TINYINT, server_default=text("0")),
    )
    pet_breed: str = Field(max_length=48, nullable=True)
    pet_color: str = Field(max_length=48, nullable=True)
    pet_birth: date | None = Field(nullable=True)
    pet_staff1: str = Field(max_length=32, nullable=True)
    pet_staff2: str = Field(max_length=32, nullable=True)
    pet_refer: str = Field(max_length=127, nullable=True)
    pet_firstdate: date | None = Field(
        default=None, sa_column=Column(Date, nullable=False, server_default=text("(CURRENT_DATE())"))
    )
    pet_lastdate: date | None = Field(
        default=None, sa_column=Column(Date, nullable=False, server_default=text("(CURRENT_DATE())"))
    )
    pet_memo1: str | None = Field(
        default=None,
        sa_column=Column(Text),  # MySQL의 TEXT 타입으로 명시적 매핑
    )
    pet_memo1_encoded: str | None = Field(
        default=None,
        sa_column=Column(Text),
    )
    pet_memo2: str | None = Field(
        default=None,
        sa_column=Column(Text),
    )
    pet_memo2_encoded: str | None = Field(
        default=None,
        sa_column=Column(Text),
    )
    pet_alert: int | None = Field(default=0, sa_column=Column(TINYINT, server_default=text("0")))
    pet_state: bool = Field(
        default=False, sa_column=Column(Boolean, nullable=False, server_default=text("0"))
    )
    pet_feed: str = Field(max_length=255, nullable=True)
    pet_default: int | None = Field(default=0, sa_column=Column(TINYINT, server_default=text("0")))
    created_sign_name: str = Field(default=None, max_length=32)
    modified_sign_name: str = Field(default=None, max_length=32)

    model_config = ConfigDict(from_attributes=True)
