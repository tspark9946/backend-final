from datetime import date
from decimal import Decimal

from pydantic import ConfigDict
from sqlalchemy.dialects.mysql import TINYINT
from sqlmodel import Boolean, Column, Date, Field, Numeric, SQLModel, Text, text


class ClientBase(SQLModel):
    client_serial: int = Field(nullable=False, index=True)
    client_name: str = Field(max_length=64, nullable=True)
    client_zip: str = Field(max_length=10, nullable=True)
    client_address1: str = Field(max_length=127, nullable=True)
    client_address2: str = Field(max_length=127, nullable=True)
    client_email: str = Field(max_length=64, nullable=True)
    client_etc: str = Field(max_length=255, nullable=True)
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
    client_state: bool = Field(
        default=False, sa_column=Column(Boolean, nullable=False, server_default=text("0"))
    )

    created_sign_name: str = Field(default=None, max_length=32)
    modified_sign_name: str = Field(default=None, max_length=32)

    model_config = ConfigDict(from_attributes=True)


class ClientCreate(ClientBase):
    model_config = {
        "json_schema_extra": {
            "example": {
                "client_serial": 12345,
                "client_name": "John Doe",
                "client_zip": "12345",
                "client_address1": "123 Main St",
                "client_address2": "Apt 4B",
                "client_email": "john.doe@example.com",
                "client_etc": "Additional information about the client",
                "client_firstdate": "2024-01-01",
                "client_debt": "100.00",
                "client_resmoney": "50.00",
                "client_point": "10.00",
                "client_memo1": "Memo 1",
                "client_memo1_encoded": "Encoded Memo 1",
                "client_memo2": "Memo 2",
                "client_memo2_encoded": "Encoded Memo 2",
                "client_alert": 1,
                "client_state": False,
                "created_sign_name": "Admin",
                "modified_sign_name": "Admin",
            }
        }
    }


class ClientResponse(ClientBase):
    client_id: int
    created_at: date | None = None
    updated_at: date | None = None


class ClientUpdate(ClientBase):
    client_id: int


class ClientDelete(SQLModel):
    client_id: int
