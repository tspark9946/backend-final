from datetime import datetime

from pydantic import ConfigDict
from sqlalchemy.ext.declarative import declared_attr
from sqlmodel import Field, SQLModel, func


def camel_to_snake(name: str) -> str:
    """
    Convert CamelCase to snake_case.
    Example:
        HospitalSign -> hospital_sign
    """
    import re

    name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()


class Base(SQLModel):
    """
    Base class with common attributes and configurations.
    """

    @declared_attr
    def __tablename__(cls) -> str:
        return camel_to_snake(cls.__name__)

    # id: int | None = Field(default=None, primary_key=True, index=True)
    # None이 기본값인 정수형 기본 키를 자동으로 AUTO_INCREMENT로 처리

    created_at: datetime = Field(
        default=None,
        sa_column_kwargs={"server_default": func.now()},
    )
    updated_at: datetime | None = Field(nullable=True)

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        # json_encoders={datetime: lambda v: v.strftime("%Y-%m-%d %H:%M")},
    )
