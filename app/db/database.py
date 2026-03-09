from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.config import settings

# Import all models to register them with SQLModel metadata, even if not used directly here
# 사용하지 않는 패키지 자동 삭제 기능을 죽이기 위해 noqa: F401 를 덧붙임
# from .models import Hospital, Sign  # noqa: F401

# 데이터베이스 연결 URL (MySQL 형식)
# mysql+pymysql://<user>:<password>@<host>:<port>/<database>
# async_engine = create_async_engine(url=settings.DATABASE_URL)
async_engine = create_async_engine(url=settings.DATABASE_URL, echo=True)


async def initdb():
    async with async_engine.begin() as conn:
        # database 연결테스트
        # statement = text("select * from user;")
        # result = await conn.execute(statement)
        # print(result.all())
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
