from datetime import datetime

from .include import (
    Hall,
    Movie,
    Session,
    Ticket,
    and_,
    BaseDatabaseDep,
    delete,
    func,
    insert,
    select,
    update,
)


class SessionService(BaseDatabaseDep):
    async def _get_row(self, session_id: int):
        stmt = (
            select(
                Session.id,
                Session.movie_id,
                Session.hall_id,
                Session.start_time,
                Session.price,
                Movie.title.label("movie_title"),
                Hall.name.label("hall_name"),
            )
            .join(Movie, Movie.id == Session.movie_id)
            .join(Hall, Hall.id == Session.hall_id)
            .where(Session.id == session_id)
        )
        return (await self.session.execute(stmt)).mappings().one_or_none()

    async def _validate_movie(self, movie_id: int):
        movie_stmt = select(Movie.id).where(Movie.id == movie_id)
        movie = (await self.session.execute(movie_stmt)).scalar_one_or_none()
        assert movie, f"Фильм с ID == {movie_id} не найден!"

    async def _validate_hall(self, hall_id: int):
        hall_stmt = select(Hall.id).where(Hall.id == hall_id)
        hall = (await self.session.execute(hall_stmt)).scalar_one_or_none()
        assert hall, f"Зал с ID == {hall_id} не найден!"

    async def create_session(self, data: dict) -> int:
        await self._validate_movie(data["movie_id"])
        await self._validate_hall(data["hall_id"])
        assert data["price"] > 0, "Цена билета должна быть больше 0"

        stmt = insert(Session).values(**data).returning(Session.id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_by_id(self, session_id: int) -> dict:
        result = await self._get_row(session_id)
        assert result, f"Сеанс с ID == {session_id} не найден!"
        return dict(result)

    async def get_all(
        self,
        page: int = 1,
        per_page: int = 10,
        movie_id: int | None = None,
        hall_id: int | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[dict]:
        offset = (page - 1) * per_page

        filters = []
        if movie_id is not None:
            filters.append(Session.movie_id == movie_id)
        if hall_id is not None:
            filters.append(Session.hall_id == hall_id)
        if date_from is not None:
            filters.append(Session.start_time >= date_from)
        if date_to is not None:
            filters.append(Session.start_time <= date_to)

        stmt = (
            select(
                Session.id,
                Session.movie_id,
                Session.hall_id,
                Session.start_time,
                Session.price,
                Movie.title.label("movie_title"),
                Hall.name.label("hall_name"),
            )
            .join(Movie, Movie.id == Session.movie_id)
            .join(Hall, Hall.id == Session.hall_id)
            .order_by(Session.start_time)
            .offset(offset)
            .limit(per_page)
        )

        if filters:
            stmt = stmt.where(and_(*filters))

        result = await self.session.execute(stmt)
        return [dict(row) for row in result.mappings().all()]

    async def get_movie_sessions(self, movie_id: int) -> list[dict]:
        await self._validate_movie(movie_id)

        stmt = (
            select(
                Session.id,
                Session.movie_id,
                Session.hall_id,
                Session.start_time,
                Session.price,
                Movie.title.label("movie_title"),
                Hall.name.label("hall_name"),
            )
            .join(Movie, Movie.id == Session.movie_id)
            .join(Hall, Hall.id == Session.hall_id)
            .where(Session.movie_id == movie_id)
            .order_by(Session.start_time)
        )
        result = await self.session.execute(stmt)
        return [dict(row) for row in result.mappings().all()]

    async def update_session(self, session_id: int, data: dict) -> bool:
        await self.get_by_id(session_id)
        assert data, "Нет полей для обновления"

        current_stmt = select(Session).where(Session.id == session_id)
        current_session = (await self.session.execute(current_stmt)).scalar_one()

        movie_id = data.get("movie_id", current_session.movie_id)
        hall_id = data.get("hall_id", current_session.hall_id)

        await self._validate_movie(movie_id)
        await self._validate_hall(hall_id)

        if "price" in data:
            assert data["price"] > 0, "Цена билета должна быть больше 0"

        stmt = (
            update(Session)
            .where(Session.id == session_id)
            .values(**data)
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return True

    async def delete_session(self, session_id: int) -> bool:
        await self.get_by_id(session_id)

        tickets_count_stmt = select(func.count(Ticket.id)).where(Ticket.session_id == session_id)
        tickets_count = (await self.session.execute(tickets_count_stmt)).scalar_one()
        assert tickets_count == 0, "Нельзя удалить сеанс, пока на него есть билеты"

        stmt = delete(Session).where(Session.id == session_id)
        await self.session.execute(stmt)
        await self.session.commit()
        return True
