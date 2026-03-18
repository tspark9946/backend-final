from datetime import date

from pydantic import ConfigDict
from sqlalchemy.dialects.mysql import TINYINT
from sqlmodel import Boolean, Column, Date, Field, SQLModel, Text, text


class PetBase(SQLModel):
    pet_serial: int = Field(nullable=False, index=True)
    pet_name: str = Field(max_length=64, nullable=True)
    pet_rfid: str | None = Field(default=None, max_length=64, nullable=True)
    #'0 : In Body, 1 : Out Body, 2 : Pendent',
    pet_rfidtype: int = Field(
        default=0,
        sa_column=Column(TINYINT, server_default=text("0")),
    )
    pet_breed: str | None = Field(default=None, max_length=48, nullable=True)
    pet_color: str | None = Field(default=None, max_length=48, nullable=True)
    pet_birth: date | None = Field(default=None, nullable=True)
    pet_staff1: str | None = Field(default=None, max_length=32, nullable=True)
    pet_staff2: str | None = Field(default=None, max_length=32, nullable=True)
    pet_refer: str | None = Field(default=None, max_length=127, nullable=True)
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
    # alert - 0 : not showing, 1 : Popup only, 2 : Popup with sound',
    pet_alert: int | None = Field(default=0, sa_column=Column(TINYINT, server_default=text("0")))
    #'0 : Normal, 1 : Deleted, 2 : Dead, 3 : Adopted',
    pet_state: int | None = Field(
        default=0, sa_column=Column(TINYINT, nullable=False, server_default=text("0"))
    )
    pet_feed: str | None = Field(default=None, max_length=255, nullable=True)
    pet_default: bool | None = Field(
        default=False, sa_column=Column(Boolean, nullable=False, server_default=text("0"))
    )

    model_config = ConfigDict(from_attributes=True)


class PetCreate(PetBase):
    client_id: int | None = None
    species_id: int | None = None
    sex_id: int | None = None
    taxfree_id: int | None = None
    created_sign_id: int | None = None
    created_sign_name: str | None = None
    hospital_id: int | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "pet_serial": 3,
                "pet_name": "다롱이",
                "pet_breed": "요크셔",
                "pet_color": "black and white",
                "pet_birth": "2020-03-13",
                "pet_memo1": "메모1 string",
                "pet_memo1_encoded": "인코딩 메모1 string",
                "pet_memo2": "메모2 string",
                "pet_memo2_encoded": "인코딩 메모2 string",
                "species_id": 1,
                "sex_id": 3,
                "taxfree_id": 2,
            }
        }
    }


class PetResponse(PetBase):
    pet_id: int | None = None
    client_id: int | None = None
    species_id: int | None = None
    sex_id: int | None = None
    taxfree_id: int | None = None
    created_sign_id: int | None = None
    created_sign_name: str | None = None
    updated_sign_id: int | None = None
    updated_sign_name: str | None = None
    hospital_id: int | None = None


class PetUpdate(PetBase):
    pet_id: int | None = None
    client_id: int | None = None
    species_id: int | None = None
    sex_id: int | None = None
    taxfree_id: int | None = None
    updated_sign_id: int | None = None
    updated_sign_name: str | None = None
    hospital_id: int | None = None


class PetDelete(SQLModel):
    pet_id: int
