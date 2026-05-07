from contextlib import asynccontextmanager
from os import getenv

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.exc import IntegrityError

from backend.database.core import init_database
from backend.database.seed import seed_initial_data


load_dotenv()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_database()
    await seed_initial_data()
    yield


app = FastAPI(
    title="CinemaHub Backend",
    debug=(getenv("DEBUG", "True").lower() == "true"),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AssertionError)
async def assertion_error_handler(_: Request, exc: AssertionError):
    logger.warning(str(exc))
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError):
    logger.warning(str(exc))
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(_: Request, exc: IntegrityError):
    logger.error(str(exc))
    return JSONResponse(
        status_code=400,
        content={"detail": "Нарушено ограничение базы данных"},
    )


__all__ = ["app"]
