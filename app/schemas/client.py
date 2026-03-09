from datetime import date, datetime
from decimal import Decimal

from pydantic import ConfigDict
from sqlalchemy.dialects.mysql import TINYINT
from sqlmodel import Boolean, Column, Date, Field, Numeric, SQLModel, Text, text


class ClientBase(SQLModel):
    client_serial: int = Field(nullable=False, index=True, unique=True)
    client_name: str | None = Field(default=None, max_length=64, nullable=True)
    client_zip: str | None = Field(default=None, max_length=10, nullable=True)
    client_address1: str | None = Field(default=None, max_length=127, nullable=True)
    client_address2: str | None = Field(default=None, max_length=127, nullable=True)
    client_email: str | None = Field(default=None, max_length=64, nullable=True)
    client_etc: str | None = Field(default=None, max_length=255, nullable=True)
    client_firstdate: date | None = Field(
        default=None, sa_column=Column(Date, nullable=False, server_default=text("(CURRENT_DATE())"))
    )
    client_debt: Decimal = Field(
        default=Decimal("0.00"), sa_column=Column(Numeric(10, 2), nullable=False, server_default=text("0.00"))
    )
    client_resmoney: Decimal = Field(
        default=Decimal("0.00"), sa_column=Column(Numeric(10, 2), nullable=False, server_default=text("0.00"))
    )
    client_point: Decimal = Field(
        default=Decimal("0.00"), sa_column=Column(Numeric(10, 2), nullable=False, server_default=text("0.00"))
    )
    client_memo1: str | None = Field(
        default=None,
        sa_column=Column(Text),
    )
    client_memo1_encoded: str | None = Field(
        default=None,
        sa_column=Column(Text),
    )
    client_memo2: str | None = Field(
        default=None,
        sa_column=Column(Text),
    )
    client_memo2_encoded: str | None = Field(
        default=None,
        sa_column=Column(Text),
    )
    # alert - 0 : not showing, 1 : Popup only, 2 : Popup with sound',
    client_alert: int | None = Field(default=0, sa_column=Column(TINYINT, server_default=text("0")))
    # state - 0: Normal, 1: Deleted
    client_state: bool | None = Field(
        default=False, sa_column=Column(Boolean, nullable=False, server_default=text("0"))
    )

    created_sign_name: str | None = Field(default=None, nullable=True, max_length=32)
    modified_sign_name: str | None = Field(default=None, nullable=True, max_length=32)

    model_config = ConfigDict(from_attributes=True)


class ClientCreate(ClientBase):
    hospital_id: int | None = Field(default=None, nullable=False)
    rank_id: int | None = Field(default=None, nullable=True)
    created_sign_id: int | None = Field(default=None, nullable=True)
    model_config = {
        "json_schema_extra": {
            "example": {
                "client_serial": 1,
                "client_name": "박현서",
                "client_zip": "12345",
                "client_address1": "서울시 도봉구 해등로 242-11",
                "client_address2": "107동 1501호",
                "client_email": "john.doe@example.com",
                "client_etc": "Additional information about the client",
                "client_memo1": "Memo 1",
                "client_memo1_encoded": "Encoded Memo 1",
                "client_memo2": "Memo 2",
                "client_memo2_encoded": "Encoded Memo 2",
                "rank_id": 1,
            }
        }
    }


class ClientResponse(ClientBase):
    client_id: int
    hospital_id: int
    rank_id: int | None = None
    created_sign_id: int | None = None
    updated_sign_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.strftime("%Y-%m-%d")},
    )


class ClientUpdate(ClientBase):
    hospital_id: int | None = None
    updated_sign_id: int | None = None


class ClientDelete(SQLModel):
    client_id: int
