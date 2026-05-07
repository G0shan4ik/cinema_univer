from backend.database.methods.favorite_methods import FavoriteService
from backend.api.security import get_current_user, require_same_user_or_admin
from backend.database.models import User

from .include import *


favorite_router = APIRouter(
    tags=["Favorites"]
)


@favorite_router.post(
    "/favorite",
    response_model=CreatedModel
)
async def create_favorite(
    favorite: FavoriteCreate,
    favorite_db: Annotated[FavoriteService, Depends(sql_helper_factory(FavoriteService))],
    current_user: Annotated[User, Depends(get_current_user)],
):
    require_same_user_or_admin(current_user, favorite.user_id)
    created_id = await favorite_db.create_favorite(
        favorite.user_id,
        favorite.movie_id,
    )
    return {"created_id": created_id}


@favorite_router.post(
    "/favorite/remove",
    response_model=StatusModel
)
async def remove_favorite(
    favorite: FavoriteCreate,
    favorite_db: Annotated[FavoriteService, Depends(sql_helper_factory(FavoriteService))],
    current_user: Annotated[User, Depends(get_current_user)],
):
    require_same_user_or_admin(current_user, favorite.user_id)
    return {
        "status": await favorite_db.delete_favorite(
            favorite.user_id,
            favorite.movie_id,
        )
    }


@favorite_router.get(
    "/favorites/{user_id}",
    response_model=list[FavoriteMovieResponse]
)
async def get_user_favorites(
    user_id: int,
    favorite_db: Annotated[FavoriteService, Depends(sql_helper_factory(FavoriteService))],
    current_user: Annotated[User, Depends(get_current_user)],
):
    require_same_user_or_admin(current_user, user_id)
    return await favorite_db.get_user_favorites(user_id)
