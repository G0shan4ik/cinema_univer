from app.database.methods.movie_methods import MovieService
from app.api.security import require_admin
from app.database.models import User

from .include import *


movie_router = APIRouter(
    tags=["Movies"]
)


@movie_router.post(
    "/movie",
    response_model=CreatedModel
)
async def create_movie(
    movie: MovieCreate,
    movie_db: Annotated[MovieService, Depends(sql_helper_factory(MovieService))],
    _: Annotated[User, Depends(require_admin)],
):
    created_id = await movie_db.create_movie(movie.model_dump())
    return {"created_id": created_id}


@movie_router.get(
    "/movie/{movie_id}",
    response_model=MovieResponse
)
async def get_movie_by_id(
    movie_id: int,
    movie_db: Annotated[MovieService, Depends(sql_helper_factory(MovieService))]
):
    return await movie_db.get_by_id(movie_id)


@movie_router.get(
    "/movies",
    response_model=list[MovieResponse]
)
async def get_movies(
    movie_db: Annotated[MovieService, Depends(sql_helper_factory(MovieService))],
    page: int = 1,
    per_page: int = 10,
    genre: str | None = None,
    search: str | None = None,
    min_rating: float | None = None,
):
    return await movie_db.get_all(
        page=page,
        per_page=per_page,
        genre=genre,
        search=search,
        min_rating=min_rating,
    )


@movie_router.patch(
    "/movie/{movie_id}",
    response_model=StatusModel
)
async def update_movie(
    movie_id: int,
    movie: MovieUpdate,
    movie_db: Annotated[MovieService, Depends(sql_helper_factory(MovieService))],
    _: Annotated[User, Depends(require_admin)],
):
    status = await movie_db.update_movie(
        movie_id,
        movie.model_dump(exclude_unset=True),
    )
    return {"status": status}


@movie_router.delete(
    "/movie/{movie_id}",
    response_model=StatusModel
)
async def delete_movie(
    movie_id: int,
    movie_db: Annotated[MovieService, Depends(sql_helper_factory(MovieService))],
    _: Annotated[User, Depends(require_admin)],
):
    return {"status": await movie_db.delete_movie(movie_id)}
