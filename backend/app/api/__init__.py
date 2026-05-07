from .core import app
from .routers import (
    hall_router,
    movie_router,
    session_router,
    ticket_router,
    user_router,
)

app.include_router(hall_router)
app.include_router(movie_router)
app.include_router(session_router)
app.include_router(ticket_router)
app.include_router(user_router)
