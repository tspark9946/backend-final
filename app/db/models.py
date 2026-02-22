from datetime import datetime

from sqlalchemy import ForeignKey
from sqlmodel import Column, Field, Integer, String

from app.schemas.sign import SignBase

from .base import Base


####################################
# Better-AUTH 에 사용하는 테이블 정의
class User(Base, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    # None이 기본값인 정수형 기본 키를 자동으로 AUTO_INCREMENT로 처리
    name: str = Field(max_length=255)
    email: str = Field(max_length=255)
    email_verified: bool = Field(default=False)
    image: str | None = Field(default=None, max_length=255)

    def __repr__(self) -> str:
        return f"<User {self.name}>"


class Session(Base, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    # None이 기본값인 정수형 기본 키를 자동으로 AUTO_INCREMENT로 처리
    token: str = Field(max_length=255)
    expires_at: datetime | None = Field(default=None)
    ip_address: str = Field(max_length=255)
    user_agent: str = Field(max_length=255)
    user_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("user.id", ondelete="NO ACTION", onupdate="NO ACTION"),
            nullable=False,
        )
    )

    def __repr__(self) -> str:
        return f"<Session {self.token}>"


class Account(Base, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    # None이 기본값인 정수형 기본 키를 자동으로 AUTO_INCREMENT로 처리
    account_id: str = Field(max_length=255)
    provider_id: str = Field(max_length=255)
    access_token: str = Field(max_length=511)
    refresh_token: str = Field(max_length=511)
    access_token_expires_at: datetime | None = Field(default=None)
    refresh_token_expires_at: datetime | None = Field(default=None)
    scope: str = Field(max_length=255)
    id_token: str = Field(max_length=255)
    password: str = Field(max_length=255)
    user_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("user.id", ondelete="NO ACTION", onupdate="NO ACTION"),
            nullable=False,
        )
    )

    def __repr__(self) -> str:
        return f"<Account {self.account_id}>"


class Verification(Base, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    # None이 기본값인 정수형 기본 키를 자동으로 AUTO_INCREMENT로 처리
    identifier: str = Field(max_length=255)
    value: str = Field(max_length=255)
    expires_at: datetime | None = Field(default=None)

    def __repr__(self) -> str:
        return f"<Verification {self.identifier}>"


##############################################


##############################################
# PMS 시스템에서 사용하는 테이블 정의
class Hospital(Base, table=True):
    __tablename__ = "HOSPITAL"
    hospital_id: int | None = Field(default=None, primary_key=True, index=True)
    # None이 기본값인 정수형 기본 키를 자동으로 AUTO_INCREMENT로 처리
    hospital_name: str = Field(max_length=64)
    hospital_master: str = Field(max_length=64)
    hospital_tel1: str = Field(max_length=64, nullable=True)
    hospital_tel2: str = Field(max_length=64, nullable=True)
    hospital_callback_tel: str = Field(max_length=64, nullable=True)
    hospital_fax: str = Field(max_length=64, nullable=True)
    hospital_email: str = Field(max_length=127, nullable=True)
    hospital_address1: str = Field(max_length=127, nullable=True)
    hospital_address2: str = Field(max_length=127, nullable=True)
    hospital_city: str = Field(max_length=64, nullable=True)
    hospital_region: str = Field(max_length=64, nullable=True)
    hospital_zip: str = Field(max_length=10, nullable=True)
    hospital_sms_count: int = Field(default=None, nullable=True)
    memo: str = Field(max_length=1023, nullable=True)
    recent_login: datetime | None = Field(default=None)
    created_by: str = Field(max_length=64, nullable=True)
    updated_by: str = Field(max_length=64, nullable=True)
    hospital_deleted: bool = Field(default=False)

    # signs: list["Sign"] = Relationship(back_populates="hospital")

    def __repr__(self) -> str:
        return f"<Hospital {self.hospital_name}>"


class Sign(Base, SignBase, table=True):
    sign_id: int | None = Field(default=None, primary_key=True, index=True)
    is_verified: bool = Field(default=False)

    sign_role: str = Field(sa_column=Column(String(20), nullable=False, server_default="user"))

    # ForeignKey Option: CASCADE, SET NULL, NO ACTION, RESTRICT, SET DEFAULT
    hospital_id: int | None = Field(
        sa_column=Column(
            Integer,
            ForeignKey("HOSPITAL.hospital_id", ondelete="NO ACTION", onupdate="CASCADE"),
            nullable=True,
        )
    )
    # async relationship 설정: lazy='selectin' (eager loading) 또는 lazy='joined' (joined loading)
    # hospital: Hospital | None = Relationship(back_populates="signs", sa_relationship_kwargs={"lazy": "selectin"} )

    def __repr__(self) -> str:
        return f"Sign(sign_name={self.sign_name!r}, sign_email={self.sign_email!r})"
