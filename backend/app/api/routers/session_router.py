from datetime import datetime

from backend.database.methods.session_methods import SessionService
from backend.database.methods.ticket_methods import TicketService
from backend.api.security import require_admin
from backend.database.models import User

from .include import *


session_router = APIRouter(
    tags=["Sessions"]
)


@session_router.post(
    "/session",
    response_model=CreatedModel
)
async def create_session(
    session: SessionCreate,
    session_db: Annotated[SessionService, Depends(sql_helper_factory(SessionService))],
    _: Annotated[User, Depends(require_admin)],
):
    created_id = await session_db.create_session(session.model_dump())
    return {"created_id": created_id}


@session_router.get(
    "/session/{session_id}",
    response_model=SessionResponse
)
async def get_session_by_id(
    session_id: int,
    session_db: Annotated[SessionService, Depends(sql_helper_factory(SessionService))]
):
    return await session_db.get_by_id(session_id)


@session_router.get(
    "/sessions",
    response_model=list[SessionResponse]
)
async def get_sessions(
    session_db: Annotated[SessionService, Depends(sql_helper_factory(SessionService))],
    page: int = 1,
    per_page: int = 10,
    movie_id: int | None = None,
    hall_id: int | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
):
    return await session_db.get_all(
        page=page,
        per_page=per_page,
        movie_id=movie_id,
        hall_id=hall_id,
        date_from=date_from,
        date_to=date_to,
    )


@session_router.get(
    "/movie/{movie_id}/sessions",
    response_model=list[SessionResponse]
)
async def get_movie_sessions(
    movie_id: int,
    session_db: Annotated[SessionService, Depends(sql_helper_factory(SessionService))]
):
    return await session_db.get_movie_sessions(movie_id)


@session_router.patch(
    "/session/{session_id}",
    response_model=StatusModel
)
async def update_session(
    session_id: int,
    session: SessionUpdate,
    session_db: Annotated[SessionService, Depends(sql_helper_factory(SessionService))],
    _: Annotated[User, Depends(require_admin)],
):
    status = await session_db.update_session(
        session_id,
        session.model_dump(exclude_unset=True),
    )
    return {"status": status}


@session_router.delete(
    "/session/{session_id}",
    response_model=StatusModel
)
async def delete_session(
    session_id: int,
    session_db: Annotated[SessionService, Depends(sql_helper_factory(SessionService))],
    _: Annotated[User, Depends(require_admin)],
):
    return {"status": await session_db.delete_session(session_id)}


@session_router.get(
    "/session/{session_id}/seats",
    response_model=SessionSeatsResponse
)
async def get_session_seats(
    session_id: int,
    ticket_db: Annotated[TicketService, Depends(sql_helper_factory(TicketService))]
):
    return await ticket_db.get_session_seats(session_id)
