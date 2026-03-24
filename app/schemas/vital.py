from datetime import date, time

from sqlmodel import Column, Date, Field, Float, SQLModel, Time, text


class VitalBase(SQLModel):
    # Core Data Fields
    vital_date: date | None = Field(
        default=None, sa_column=Column(Date, nullable=False, server_default=text("(CURDATE())"))
    )
    vital_time: time | None = Field(
        default=None, sa_column=Column(Time, nullable=False, server_default=text("CURTIME()"))
    )
    # Vital Signs (Nullable floats)
    vital_bw: float | None = Field(default=None, description="Body Weight")
    vital_bt: float | None = Field(default=None, description="Body Temperature")
    vital_bp: float | None = Field(default=None, description="Blood Pressure (systolic)")
    vital_bp2: float | None = Field(
        default=0.0,
        sa_column=Column(Float, nullable=False, server_default=text("0")),
        description="Blood Pressure (diastolic)",
    )
    vital_hr: float | None = Field(default=None, description="Heart Rate")
    vital_rr: float | None = Field(
        default=0.0,
        sa_column=Column(Float, nullable=False, server_default=text("0")),
        description="Respiration Rate",
    )
    vital_bcs: float | None = Field(default=None, description="BCS(Body Condition Score)")

    vital_memo: str | None = Field(default=None, max_length=255)


class VitalCreate(VitalBase):
    pet_id: int | None = None
    created_sign_id: int | None = None
    created_sign_name: str | None = None
    hospital_id: int | None = None


class VitalResponse(VitalBase):
    vital_id: int | None = None
    pet_id: int | None = None
    created_sign_id: int | None = None
    created_sign_name: str | None = None
    updated_sign_id: int | None = None
    updated_sign_name: str | None = None
    hospital_id: int | None = None


class VitalUpdate(VitalBase):
    vital_id: int | None = None
    updated_sign_id: int | None = None
    updated_sign_name: str | None = None
    hospital_id: int | None = None


class VitalDelete(SQLModel):
    vital_id: int
