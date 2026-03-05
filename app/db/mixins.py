from datetime import datetime

from pydantic import ConfigDict
from sqlalchemy import text
from sqlalchemy.ext.declarative import declared_attr
from sqlmodel import Field, SQLModel


def camel_to_snake(name: str) -> str:
    """
    Convert CamelCase to snake_case.
    Example:
        HospitalSign -> hospital_sign
    """
    import re

    name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()


class TimestampMixin(SQLModel):
    """
    Base class with common attributes and configurations.
    """

    @declared_attr
    def __tablename__(cls) -> str:
        return camel_to_snake(cls.__name__)

    # created_at과 updated_at 필드는 모든 모델에서 공통적으로 사용되며, 자동으로 현재 시간으로 설정됩니다.
    # mixin을 상속받는 각 모델에서 필드가 생성되기 위해 sa_column -> sa_column_kwargs로 변경
    order_idx: int | None = Field(default=None)

    created_at: datetime = Field(
        sa_column_kwargs={
            "nullable": False,
            "server_default": text("CURRENT_TIMESTAMP"),
        }
    )

    updated_at: datetime = Field(
        default=None,
        sa_column_kwargs={
            "nullable": True,
            "server_default": text("NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP"),
        },
    )

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
    )
