from .include import (
    Favorite,
    Movie,
    User,
    BaseDatabaseDep,
    delete,
    insert,
    select,
)


class FavoriteService(BaseDatabaseDep):
    async def create_favorite(self, user_id: int, movie_id: int) -> int:
        user_stmt = select(User.id).where(User.id == user_id)
        movie_stmt = select(Movie.id).where(Movie.id == movie_id)

        user = (await self.session.execute(user_stmt)).scalar_one_or_none()
        movie = (await self.session.execute(movie_stmt)).scalar_one_or_none()

        assert user, f"Пользователь с ID == {user_id} не найден!"
        assert movie, f"Фильм с ID == {movie_id} не найден!"

        exists_stmt = select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.movie_id == movie_id,
        )
        exists = (await self.session.execute(exists_stmt)).scalar_one_or_none()
        assert not exists, "Фильм уже добавлен в избранное"

        stmt = insert(Favorite).values(
            user_id=user_id,
            movie_id=movie_id,
        ).returning(Favorite.id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def delete_favorite(self, user_id: int, movie_id: int) -> bool:
        stmt = select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.movie_id == movie_id,
        )
        favorite = (await self.session.execute(stmt)).scalar_one_or_none()
        assert favorite, "Избранный фильм не найден"

        delete_stmt = delete(Favorite).where(Favorite.id == favorite.id)
        await self.session.execute(delete_stmt)
        await self.session.commit()
        return True

    async def get_user_favorites(self, user_id: int) -> list[dict]:
        user_stmt = select(User.id).where(User.id == user_id)
        user = (await self.session.execute(user_stmt)).scalar_one_or_none()
        assert user, f"Пользователь с ID == {user_id} не найден!"

        stmt = (
            select(
                Favorite.id.label("favorite_id"),
                Movie.id.label("movie_id"),
                Movie.title,
                Movie.description,
                Movie.genre,
                Movie.duration_minutes,
                Movie.rating,
                Movie.poster_url,
                Movie.release_date,
            )
            .join(Movie, Movie.id == Favorite.movie_id)
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.id.desc())
        )
        result = await self.session.execute(stmt)
        return [dict(row) for row in result.mappings().all()]
