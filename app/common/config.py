from typing import List

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    debug: bool = False
    db_user: str = ""
    db_password: str = ""
    db_name: str = "test.db"
    db_host: str = "localhost"
    ALLOWED_ORIGINS: str = ""
    JWT_SECRET: str
    JWT_ALGORITHM: str

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = ""

    @property
    def DATABASE_URL(self):
        return f"mysql+aiomysql://{self.db_user}:{self.db_password}@{self.db_host}/{self.db_name}?charset=utf8mb4"

    @field_validator("ALLOWED_ORIGINS")
    def parse_allowed_origins(cls, v: str) -> List[str]:
        return v.split(",") if v else []

    # model_config = SettingsConfigDict(
    #     env_file = ".env",
    #     env_file_encoding = "utf-8",
    #     case_sensitive = False
    # )


settings = Settings()
