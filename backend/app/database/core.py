import sys
from os import getenv

from loguru import logger
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
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
        await connection.run_sync(Base.metadata.drop_all)

        await connection.run_sync(Base.metadata.create_all)
        await connection.run_sync(_ensure_user_table_columns)
        logger.debug(
            "Created tables: " + (", ".join(i for i in Base.metadata.tables))
        )


def _ensure_user_table_columns(connection):
    inspector = inspect(connection)
    if "users" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("users")}
    missing_columns = {
        "keyword_hash": "ALTER TABLE users ADD COLUMN keyword_hash VARCHAR(60)",
        "secret_question": "ALTER TABLE users ADD COLUMN secret_question VARCHAR(255)",
        "secret_answer_hash": "ALTER TABLE users ADD COLUMN secret_answer_hash VARCHAR(60)",
    }

    for column_name, ddl in missing_columns.items():
        if column_name not in existing_columns:
            connection.exec_driver_sql(ddl)
            logger.info(f"Added missing column users.{column_name}")


async def init():
    await init_database()


if __name__ == '__main__':
    import asyncio

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(init())
