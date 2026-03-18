from typing import Annotated

from pydantic import BeforeValidator


# 정수(0, 1)를 불리언으로 안전하게 변환하는 로직
def cast_int_to_bool(v):
    if isinstance(v, int) and not isinstance(v, bool):
        return bool(v)
    return v


# 재사용 가능한 "TINYINT용 불리언" 타입
TINYINT_BOOL = Annotated[bool, BeforeValidator(cast_int_to_bool)]
