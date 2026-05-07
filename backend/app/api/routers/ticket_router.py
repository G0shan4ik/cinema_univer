from app.database.methods.ticket_methods import TicketService
from app.api.security import get_current_user, require_admin, require_same_user_or_admin
from app.database.models import User, UserRole
from fastapi import HTTPException, status

from .include import *


ticket_router = APIRouter(
    tags=["Tickets"]
)


@ticket_router.post(
    "/ticket",
    response_model=CreatedModel
)
async def create_ticket(
    ticket: TicketCreate,
    ticket_db: Annotated[TicketService, Depends(sql_helper_factory(TicketService))],
    current_user: Annotated[User, Depends(get_current_user)],
):
    require_same_user_or_admin(current_user, ticket.user_id)
    created_id = await ticket_db.create_ticket(ticket.model_dump())
    return {"created_id": created_id}


@ticket_router.get(
    "/ticket/{ticket_id}",
    response_model=TicketResponse
)
async def get_ticket_by_id(
    ticket_id: int,
    ticket_db: Annotated[TicketService, Depends(sql_helper_factory(TicketService))]
):
    return await ticket_db.get_by_id(ticket_id)


@ticket_router.get(
    "/tickets/user/{user_id}",
    response_model=list[TicketDetailResponse]
)
async def get_user_tickets(
    user_id: int,
    ticket_db: Annotated[TicketService, Depends(sql_helper_factory(TicketService))],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = 1,
    per_page: int = 10,
):
    require_same_user_or_admin(current_user, user_id)
    return await ticket_db.get_user_tickets(user_id, page, per_page)


@ticket_router.get(
    "/tickets",
    response_model=list[TicketDetailResponse]
)
async def get_tickets(
    ticket_db: Annotated[TicketService, Depends(sql_helper_factory(TicketService))],
    _: Annotated[User, Depends(require_admin)],
    page: int = 1,
    per_page: int = 20,
    user_id: int | None = None,
    session_id: int | None = None,
    status_value: TicketStatus | None = None,
):
    return await ticket_db.get_all_tickets(
        page=page,
        per_page=per_page,
        user_id=user_id,
        session_id=session_id,
        status_value=status_value,
    )


@ticket_router.get(
    "/tickets/session/{session_id}",
    response_model=list[TicketResponse]
)
async def get_session_tickets(
    session_id: int,
    ticket_db: Annotated[TicketService, Depends(sql_helper_factory(TicketService))],
    _: Annotated[User, Depends(require_admin)],
):
    return await ticket_db.get_session_tickets(session_id)


@ticket_router.patch(
    "/ticket/{ticket_id}/status",
    response_model=StatusModel
)
async def update_ticket_status(
    ticket_id: int,
    data: TicketStatusUpdate,
    ticket_db: Annotated[TicketService, Depends(sql_helper_factory(TicketService))],
    _: Annotated[User, Depends(require_admin)],
):
    return {"status": await ticket_db.update_status(ticket_id, data.status)}


@ticket_router.post(
    "/ticket/{ticket_id}/cancel",
    response_model=StatusModel
)
async def cancel_ticket(
    ticket_id: int,
    ticket_db: Annotated[TicketService, Depends(sql_helper_factory(TicketService))],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ticket = await ticket_db.get_by_id(ticket_id)
    if current_user.role != UserRole.ADMIN and ticket.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для отмены билета.",
        )
    return {"status": await ticket_db.cancel_ticket(ticket_id)}
