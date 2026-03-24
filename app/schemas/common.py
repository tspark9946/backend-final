from datetime import date

from pydantic import BaseModel, model_validator


# 1. 쿼리 파라미터를 담을 모델 정의
class DateRange(BaseModel):
    start_date: date | None = None
    end_date: date | None = None

    # 2. 필드 간 유효성 검사 로직 (Pydantic v2 방식)
    @model_validator(mode="after")
    def check_date_range(self) -> "DateRange":
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValueError("시작일(start_date)은 종료일(end_date)보다 빨라야 합니다.")
        return self
