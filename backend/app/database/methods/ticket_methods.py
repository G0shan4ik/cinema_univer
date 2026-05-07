from datetime import datetime

from .include import (
    Hall,
    Movie,
    Session,
    Ticket,
    TicketStatus,
    User,
    BaseDatabaseDep,
    insert,
    select,
    update,
)


class TicketService(BaseDatabaseDep):
    async def _get_session_with_hall(self, session_id: int):
        stmt = (
            select(
                Session.id,
                Session.movie_id,
                Session.hall_id,
                Session.start_time,
                Session.price,
                Hall.name.label("hall_name"),
                Hall.total_rows,
                Hall.seats_per_row,
            )
            .join(Hall, Hall.id == Session.hall_id)
            .where(Session.id == session_id)
        )
        return (await self.session.execute(stmt)).mappings().one_or_none()

    async def _validate_user(self, user_id: int):
        stmt = select(User).where(User.id == user_id)
        user = (await self.session.execute(stmt)).scalar_one_or_none()
        assert user, f"Пользователь с ID == {user_id} не найден!"
        assert user.is_active, "Аккаунт деактивирован!"
        return user

    async def create_ticket(self, data: dict) -> int:
        await self._validate_user(data["user_id"])
        session_data = await self._get_session_with_hall(data["session_id"])
        assert session_data, f"Сеанс с ID == {data['session_id']} не найден!"

        assert 1 <= data["seat_row"] <= session_data["total_rows"], "Некорректный ряд"
        assert 1 <= data["seat_number"] <= session_data["seats_per_row"], "Некорректное место"

        stmt = select(Ticket).where(
            Ticket.session_id == data["session_id"],
            Ticket.seat_row == data["seat_row"],
            Ticket.seat_number == data["seat_number"],
        )
        existing_ticket = (await self.session.execute(stmt)).scalar_one_or_none()

        if existing_ticket:
            assert existing_ticket.status == TicketStatus.CANCELLED, "Это место уже занято"

            reuse_stmt = (
                update(Ticket)
                .where(Ticket.id == existing_ticket.id)
                .values(
                    user_id=data["user_id"],
                    status=TicketStatus.BOOKED,
                    created_at=datetime.utcnow(),
                )
                .returning(Ticket.id)
            )
            result = await self.session.execute(reuse_stmt)
            await self.session.commit()
            return result.scalar_one()

        create_stmt = insert(Ticket).values(
            **data,
            status=TicketStatus.BOOKED,
        ).returning(Ticket.id)
        result = await self.session.execute(create_stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_by_id(self, ticket_id: int) -> Ticket:
        stmt = select(Ticket).where(Ticket.id == ticket_id)
        result = (await self.session.execute(stmt)).scalar_one_or_none()

        assert result, f"Билет с ID == {ticket_id} не найден!"
        return result

    async def get_user_tickets(
        self,
        user_id: int,
        page: int = 1,
        per_page: int = 10,
    ) -> list[dict]:
        await self._validate_user(user_id)
        offset = (page - 1) * per_page

        stmt = (
            select(
                Ticket.id,
                Ticket.user_id,
                Ticket.session_id,
                Ticket.seat_row,
                Ticket.seat_number,
                Ticket.status,
                Ticket.created_at,
                Movie.id.label("movie_id"),
                Movie.title.label("movie_title"),
                Hall.id.label("hall_id"),
                Hall.name.label("hall_name"),
                Session.start_time,
                Session.price,
            )
            .join(Session, Session.id == Ticket.session_id)
            .join(Movie, Movie.id == Session.movie_id)
            .join(Hall, Hall.id == Session.hall_id)
            .where(Ticket.user_id == user_id)
            .order_by(Ticket.created_at.desc())
            .offset(offset)
            .limit(per_page)
        )
        result = await self.session.execute(stmt)
        return [dict(row) for row in result.mappings().all()]

    async def get_all_tickets(
        self,
        page: int = 1,
        per_page: int = 20,
        user_id: int | None = None,
        session_id: int | None = None,
        status_value: TicketStatus | None = None,
    ) -> list[dict]:
        offset = (page - 1) * per_page

        stmt = (
            select(
                Ticket.id,
                Ticket.user_id,
                Ticket.session_id,
                Ticket.seat_row,
                Ticket.seat_number,
                Ticket.status,
                Ticket.created_at,
                Movie.id.label("movie_id"),
                Movie.title.label("movie_title"),
                Hall.id.label("hall_id"),
                Hall.name.label("hall_name"),
                Session.start_time,
                Session.price,
            )
            .join(Session, Session.id == Ticket.session_id)
            .join(Movie, Movie.id == Session.movie_id)
            .join(Hall, Hall.id == Session.hall_id)
            .order_by(Ticket.created_at.desc())
            .offset(offset)
            .limit(per_page)
        )

        if user_id is not None:
            stmt = stmt.where(Ticket.user_id == user_id)
        if session_id is not None:
            stmt = stmt.where(Ticket.session_id == session_id)
        if status_value is not None:
            stmt = stmt.where(Ticket.status == status_value)

        result = await self.session.execute(stmt)
        return [dict(row) for row in result.mappings().all()]

    async def get_session_tickets(self, session_id: int) -> list[Ticket]:
        session_data = await self._get_session_with_hall(session_id)
        assert session_data, f"Сеанс с ID == {session_id} не найден!"

        stmt = (
            select(Ticket)
            .where(Ticket.session_id == session_id)
            .order_by(Ticket.seat_row, Ticket.seat_number)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_status(self, ticket_id: int, status: TicketStatus) -> bool:
        await self.get_by_id(ticket_id)

        stmt = (
            update(Ticket)
            .where(Ticket.id == ticket_id)
            .values(status=status)
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return True

    async def cancel_ticket(self, ticket_id: int) -> bool:
        return await self.update_status(ticket_id, TicketStatus.CANCELLED)

    async def get_session_seats(self, session_id: int) -> dict:
        session_data = await self._get_session_with_hall(session_id)
        assert session_data, f"Сеанс с ID == {session_id} не найден!"

        stmt = (
            select(
                Ticket.seat_row,
                Ticket.seat_number,
                Ticket.status,
            )
            .where(
                Ticket.session_id == session_id,
                Ticket.status != TicketStatus.CANCELLED,
            )
            .order_by(Ticket.seat_row, Ticket.seat_number)
        )
        result = await self.session.execute(stmt)

        return {
            "session_id": session_id,
            "hall_id": session_data["hall_id"],
            "total_rows": session_data["total_rows"],
            "seats_per_row": session_data["seats_per_row"],
            "occupied_seats": [dict(row) for row in result.mappings().all()],
        }
