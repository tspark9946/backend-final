from datetime import datetime

from sqlmodel import Boolean, Column, Field, ForeignKey, Integer, SQLModel, String, text

from app.schemas.client import ClientBase
from app.schemas.pet import PetBase
from app.schemas.sign import SignBase
from app.schemas.tel import TelBase

from .mixins import TimestampMixin


####################################
# Better-AUTH 에 사용하는 테이블 정의
class User(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    # None이 기본값인 정수형 기본 키를 자동으로 AUTO_INCREMENT로 처리
    name: str = Field(max_length=255)
    email: str = Field(max_length=255)
    email_verified: bool = Field(default=False)
    image: str | None = Field(default=None, max_length=255)

    def __repr__(self) -> str:
        return f"<User {self.name}>"


class Session(TimestampMixin, table=True):
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


class Account(TimestampMixin, table=True):
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


class Verification(TimestampMixin, table=True):
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
class Hospital(TimestampMixin, table=True):
    __tablename__ = "HOSPITAL"
    hospital_id: int | None = Field(default=None, primary_key=True, index=True)
    hospital_name: str = Field(max_length=64, nullable=True)
    hospital_master: str = Field(max_length=64, nullable=True)
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
    hospital_business_registration_number: str = Field(max_length=64, nullable=True)
    hospital_sms_count: int = Field(default=None, nullable=True)
    memo: str = Field(max_length=1023, nullable=True)
    recent_login: datetime | None = Field(default=None)
    created_by: str = Field(max_length=64, nullable=True)
    updated_by: str = Field(max_length=64, nullable=True)
    hospital_deleted: bool = Field(
        default=False, sa_column=Column(Boolean, nullable=False, server_default=text("0"))
    )

    # signs: list["Sign"] = Relationship(back_populates="hospital")

    def __repr__(self) -> str:
        return f"<Hospital {self.hospital_name}>"


class Sign(TimestampMixin, SignBase, table=True):
    sign_id: int | None = Field(default=None, primary_key=True, index=True)
    is_verified: bool = Field(
        default=False, sa_column=Column(Boolean, nullable=False, server_default=text("0"))
    )

    sign_role: str = Field(sa_column=Column(String(20), nullable=False, server_default="user"))

    # ForeignKey Option: CASCADE, SET NULL, NO ACTION, RESTRICT, SET DEFAULT
    hospital_id: int | None = Field(
        sa_column=Column(
            Integer,
            ForeignKey("HOSPITAL.hospital_id", ondelete="NO ACTION", onupdate="CASCADE"),
            nullable=False,
        )
    )
    # async relationship 설정: lazy='selectin' (eager loading) 또는 lazy='joined' (joined loading)
    # hospital: Hospital | None = Relationship(back_populates="signs", sa_relationship_kwargs={"lazy": "selectin"} )

    def __repr__(self) -> str:
        return f"Sign(sign_name={self.sign_name!r}, sign_email={self.sign_email!r})"


class Rank(TimestampMixin, table=True):
    rank_id: int | None = Field(default=None, primary_key=True, index=True)
    rank_name: str = Field(max_length=64)
    rank_default: int = Field(default=0)
    order_idx: int = Field(default=None, nullable=True)
    hospital_id: int | None = Field(
        sa_column=Column(
            Integer,
            ForeignKey("HOSPITAL.hospital_id", ondelete="NO ACTION", onupdate="NO ACTION"),
            nullable=False,
        )
    )

    def __repr__(self) -> str:
        return f"<Rank {self.rank_name}>"


class Client(TimestampMixin, ClientBase, table=True):
    client_id: int | None = Field(default=None, primary_key=True, index=True)

    created_sign_id: int | None = Field(
        sa_column=Column(
            Integer,
            ForeignKey("sign.sign_id", ondelete="NO ACTION", onupdate="NO ACTION"),
            nullable=True,
        )
    )
    updated_sign_id: int | None = Field(
        sa_column=Column(
            Integer,
            ForeignKey("sign.sign_id", ondelete="SET NULL", onupdate="CASCADE"),
            nullable=True,
        )
    )
    rank_id: int | None = Field(
        sa_column=Column(
            Integer,
            ForeignKey("rank.rank_id", ondelete="SET NULL", onupdate="CASCADE"),
            nullable=True,
        )
    )
    hospital_id: int | None = Field(
        sa_column=Column(
            Integer,
            ForeignKey("HOSPITAL.hospital_id", ondelete="NO ACTION", onupdate="NO ACTION"),
            nullable=False,
        )
    )

    def __repr__(self) -> str:
        return f"<Client {self.client_name}>"


class Tel(TimestampMixin, TelBase, table=True):
    tel_id: int | None = Field(default=None, primary_key=True, index=True)

    created_sign_id: int | None = Field(
        sa_column=Column(
            Integer,
            ForeignKey("sign.sign_id", ondelete="NO ACTION", onupdate="NO ACTION"),
            nullable=True,
        )
    )
    updated_sign_id: int | None = Field(
        sa_column=Column(
            Integer,
            ForeignKey("sign.sign_id", ondelete="SET NULL", onupdate="CASCADE"),
            nullable=True,
        )
    )
    hospital_id: int | None = Field(
        sa_column=Column(
            Integer,
            ForeignKey("HOSPITAL.hospital_id", ondelete="NO ACTION", onupdate="NO ACTION"),
            nullable=False,
        )
    )

    def __repr__(self) -> str:
        return f"<Tel {self.tel_number}>"


class Locale(SQLModel, table=True):
    __tablename__ = "LOCALE"
    locale_id: int | None = Field(default=None, primary_key=True, index=True)
    locale_name: str = Field(default=None, max_length=32, nullable=True)
    locale_desc: str = Field(default=None, max_length=64, nullable=True)

    def __repr__(self) -> str:
        return f"<Locale {self.locale_name}>"


class Species(SQLModel, table=True):
    __tablename__ = "SPECIES"
    species_id: int | None = Field(default=None, primary_key=True, index=True)
    species_identifier: str = Field(default=None, max_length=32, nullable=True)
    species_name: str = Field(default=None, max_length=45, nullable=True)

    def __repr__(self) -> str:
        return f"<Species {self.name}>"


class SpeciesLocale(SQLModel, table=True):
    __tablename__ = "SPECIESLOCALE"
    species_id: int | None = Field(
        sa_column=Column(
            Integer,
            ForeignKey("SPECIES.species_id", ondelete="CASCADE", onupdate="CASCADE"),
            primary_key=True,
            nullable=False,
        )
    )
    locale_id: int | None = Field(
        sa_column=Column(
            Integer,
            ForeignKey("LOCALE.locale_id", ondelete="CASCADE", onupdate="CASCADE"),
            primary_key=True,
            nullable=False,
        )
    )
    specieslocale_name: str = Field(default=None, max_length=45, nullable=True)

    def __repr__(self) -> str:
        return f"<SpeciesLocale {self.specieslocale_name}>"


class Breed(SQLModel, table=True):
    __tablename__ = "BREED"
    breed_id: int | None = Field(default=None, primary_key=True, index=True)
    species_id: int | None = Field(
        sa_column=Column(
            Integer,
            ForeignKey("SPECIES.species_id", ondelete="CASCADE", onupdate="CASCADE"),
            nullable=False,
        )
    )
    breed_name: str = Field(default=None, max_length=127, nullable=True)
    breed_engname: str = Field(default=None, max_length=127, nullable=True)

    def __repr__(self) -> str:
        return f"<Breed {self.breed_name}>"


class Sex(SQLModel, table=True):
    __tablename__ = "SEX"
    sex_id: int | None = Field(default=None, primary_key=True, index=True)
    sex_identifier: str = Field(default=None, max_length=32, nullable=True)
    sex_name: str = Field(default=None, max_length=45, nullable=True)

    def __repr__(self) -> str:
        return f"<Sex {self.sex_name}>"


class SexLocale(SQLModel, table=True):
    __tablename__ = "SEXLOCALE"
    sex_id: int | None = Field(
        sa_column=Column(
            Integer,
            ForeignKey("SEX.sex_id", ondelete="CASCADE", onupdate="CASCADE"),
            primary_key=True,
            nullable=False,
        )
    )
    locale_id: int | None = Field(
        sa_column=Column(
            Integer,
            ForeignKey("LOCALE.locale_id", ondelete="CASCADE", onupdate="CASCADE"),
            primary_key=True,
            nullable=False,
        )
    )
    sexlocale_name: str = Field(default=None, max_length=45, nullable=True)

    def __repr__(self) -> str:
        return f"<SexLocale {self.sexlocale_name}>"


class Texfreetype(SQLModel, table=True):
    __tablename__ = "TEXFREETYPE"
    texfreetype_id: int | None = Field(default=None, primary_key=True, index=True)
    texfreetype_name: str = Field(default=None, max_length=127, nullable=True)

    def __repr__(self) -> str:
        return f"<Texfreetype {self.texfreetype_name}>"


class Pet(TimestampMixin, PetBase, table=True):
    pet_id: int | None = Field(default=None, primary_key=True, index=True)

    client_id: int | None = Field(
        sa_column=Column(
            Integer,
            ForeignKey("client.client_id", ondelete="NO ACTION", onupdate="NO ACTION"),
            nullable=False,
        )
    )
    species_id: int | None = Field(
        sa_column=Column(
            Integer,
            ForeignKey("SPECIES.species_id", ondelete="SET NULL", onupdate="CASCADE"),
            nullable=True,
        )
    )
    sex_id: int | None = Field(
        sa_column=Column(
            Integer,
            ForeignKey("SEX.sex_id", ondelete="SET NULL", onupdate="CASCADE"),
            nullable=True,
        )
    )
    taxfree_id: int | None = Field(
        sa_column=Column(
            Integer,
            ForeignKey("TEXFREETYPE.texfreetype_id", ondelete="SET NULL", onupdate="CASCADE"),
            nullable=True,
        )
    )
    created_sign_id: int | None = Field(
        sa_column=Column(
            Integer,
            ForeignKey("sign.sign_id", ondelete="NO ACTION", onupdate="NO ACTION"),
            nullable=True,
        )
    )
    created_sign_id: int | None = Field(
        sa_column=Column(
            Integer,
            ForeignKey("sign.sign_id", ondelete="NO ACTION", onupdate="NO ACTION"),
            nullable=True,
        )
    )
    updated_sign_id: int | None = Field(
        sa_column=Column(
            Integer,
            ForeignKey("sign.sign_id", ondelete="SET NULL", onupdate="CASCADE"),
            nullable=True,
        )
    )
    hospital_id: int | None = Field(
        sa_column=Column(
            Integer,
            ForeignKey("HOSPITAL.hospital_id", ondelete="NO ACTION", onupdate="NO ACTION"),
            nullable=False,
        )
    )

    def __repr__(self) -> str:
        return f"<Pet {self.pet_name}>"
