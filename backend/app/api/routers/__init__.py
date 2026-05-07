from fastapi import FastAPI

from .favorite_router import favorite_router
from .hall_router import hall_router
from .movie_router import movie_router
from .session_router import session_router
from .ticket_router import ticket_router
from .user_router import user_router


ROUTERS = (
    user_router,
    movie_router,
    hall_router,
    session_router,
    ticket_router,
    favorite_router,
)


def include_routers(app: FastAPI):
    for router in ROUTERS:
        app.include_router(router)


__all__ = [
    "include_routers",
    "ROUTERS",
]
