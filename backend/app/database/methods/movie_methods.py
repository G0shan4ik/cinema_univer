from .include import (
    Favorite,
    Movie,
    Session,
    BaseDatabaseDep,
    delete,
    func,
    insert,
    select,
    update,
)


class MovieService(BaseDatabaseDep):
    async def create_movie(self, data: dict) -> int:
        assert data["duration_minutes"] > 0, "Длительность фильма должна быть больше 0"

        stmt = insert(Movie).values(**data).returning(Movie.id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_by_id(self, movie_id: int) -> Movie:
        stmt = select(Movie).where(Movie.id == movie_id)
        result = (await self.session.execute(stmt)).scalar_one_or_none()

        assert result, f"Фильм с ID == {movie_id} не найден!"
        return result

    async def get_all(
        self,
        page: int = 1,
        per_page: int = 10,
        genre: str | None = None,
        search: str | None = None,
        min_rating: float | None = None,
    ) -> list[Movie]:
        offset = (page - 1) * per_page

        stmt = select(Movie)

        if genre:
            stmt = stmt.where(Movie.genre == genre)

        if search:
            stmt = stmt.where(Movie.title.ilike(f"%{search}%"))

        if min_rating is not None:
            stmt = stmt.where(Movie.rating >= min_rating)

        stmt = stmt.order_by(Movie.id.desc()).offset(offset).limit(per_page)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_movie(self, movie_id: int, data: dict) -> bool:
        await self.get_by_id(movie_id)
        assert data, "Нет полей для обновления"

        if "duration_minutes" in data:
            assert data["duration_minutes"] > 0, "Длительность фильма должна быть больше 0"

        stmt = (
            update(Movie)
            .where(Movie.id == movie_id)
            .values(**data)
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return True

    async def delete_movie(self, movie_id: int) -> bool:
        await self.get_by_id(movie_id)

        sessions_count_stmt = select(func.count(Session.id)).where(Session.movie_id == movie_id)
        sessions_count = (await self.session.execute(sessions_count_stmt)).scalar_one()
        assert sessions_count == 0, "Нельзя удалить фильм, пока у него есть сеансы"

        favorites_count_stmt = select(func.count(Favorite.id)).where(Favorite.movie_id == movie_id)
        favorites_count = (await self.session.execute(favorites_count_stmt)).scalar_one()
        assert favorites_count == 0, "Нельзя удалить фильм, пока он есть в избранном"

        stmt = delete(Movie).where(Movie.id == movie_id)
        await self.session.execute(stmt)
        await self.session.commit()
        return True
