import sys
from os import getenv

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from loguru import logger
from sqlalchemy.orm import DeclarativeBase

from dotenv import load_dotenv

load_dotenv()


class Base(DeclarativeBase):
    pass


USER = getenv("POSTGRES_USER", "postgres")
PASSWORD = getenv("POSTGRES_PASSWORD", "postgres")
HOST = getenv("POSTGRES_HOST", "localhost")
PORT = getenv("POSTGRES_PORT", "5432")
DB = getenv("POSTGRES_DB", "cinema")
DEBUG = getenv("DEBUG", "True").lower() == "true"
DATABASE_URL = getenv("DATABASE_URL")

if DATABASE_URL:
    database_url = DATABASE_URL
else:
    uri = f"{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"
    database_url = f"postgresql+psycopg_async://{uri}"

engine = create_async_engine(
    url=database_url,
    echo=DEBUG
)

session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)


async def init_database():
    async with engine.begin() as connection:

        # await connection.run_sync(Base.metadata.drop_all)

        await connection.run_sync(Base.metadata.create_all)
        logger.debug(
            "Created tables: " + (", ".join(i for i in Base.metadata.tables))
        )


async def init():
    await init_database()


if __name__ == '__main__':
    import asyncio

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(init())
