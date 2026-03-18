from pydantic import BaseModel


class EmailModel(BaseModel):
    address: list[str]

    model_config = {"json_schema_extra": {"example": {"address": ["parktaeseong@naver.com"]}}}
