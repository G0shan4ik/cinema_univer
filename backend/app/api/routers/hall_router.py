from app.database.methods.hall_methods import HallService
from app.api.security import require_admin
from app.database.models import User

from .include import *


hall_router = APIRouter(
    tags=["Halls"]
)


@hall_router.post(
    "/hall",
    response_model=CreatedModel
)
async def create_hall(
    hall: HallCreate,
    hall_db: Annotated[HallService, Depends(sql_helper_factory(HallService))],
    _: Annotated[User, Depends(require_admin)],
):
    created_id = await hall_db.create_hall(hall.model_dump())
    return {"created_id": created_id}


@hall_router.get(
    "/hall/{hall_id}",
    response_model=HallResponse
)
async def get_hall_by_id(
    hall_id: int,
    hall_db: Annotated[HallService, Depends(sql_helper_factory(HallService))]
):
    return await hall_db.get_by_id(hall_id)


@hall_router.get(
    "/halls",
    response_model=list[HallResponse]
)
async def get_halls(
    hall_db: Annotated[HallService, Depends(sql_helper_factory(HallService))]
):
    return await hall_db.get_all()


@hall_router.patch(
    "/hall/{hall_id}",
    response_model=StatusModel
)
async def update_hall(
    hall_id: int,
    hall: HallUpdate,
    hall_db: Annotated[HallService, Depends(sql_helper_factory(HallService))],
    _: Annotated[User, Depends(require_admin)],
):
    status = await hall_db.update_hall(
        hall_id,
        hall.model_dump(exclude_unset=True),
    )
    return {"status": status}


@hall_router.delete(
    "/hall/{hall_id}",
    response_model=StatusModel
)
async def delete_hall(
    hall_id: int,
    hall_db: Annotated[HallService, Depends(sql_helper_factory(HallService))],
    _: Annotated[User, Depends(require_admin)],
):
    return {"status": await hall_db.delete_hall(hall_id)}
