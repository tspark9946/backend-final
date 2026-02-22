from typing import List

from pydantic import BaseModel


class EmailModel(BaseModel):
    address: List[str]

    model_config = {"json_schema_extra": {"example": {"address": ["parktaeseong@naver.com"]}}}
