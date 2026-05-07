from .include import (
    Hall,
    Session,
    BaseDatabaseDep,
    delete,
    func,
    insert,
    select,
    update,
)


class HallService(BaseDatabaseDep):
    async def create_hall(self, data: dict) -> int:
        assert data["total_rows"] > 0, "В зале должен быть хотя бы 1 ряд"
        assert data["seats_per_row"] > 0, "В ряду должно быть хотя бы 1 место"

        stmt = insert(Hall).values(**data).returning(Hall.id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_by_id(self, hall_id: int) -> Hall:
        stmt = select(Hall).where(Hall.id == hall_id)
        result = (await self.session.execute(stmt)).scalar_one_or_none()

        assert result, f"Зал с ID == {hall_id} не найден!"
        return result

    async def get_all(self) -> list[Hall]:
        stmt = select(Hall).order_by(Hall.id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_hall(self, hall_id: int, data: dict) -> bool:
        await self.get_by_id(hall_id)
        assert data, "Нет полей для обновления"

        if "total_rows" in data:
            assert data["total_rows"] > 0, "В зале должен быть хотя бы 1 ряд"

        if "seats_per_row" in data:
            assert data["seats_per_row"] > 0, "В ряду должно быть хотя бы 1 место"

        stmt = (
            update(Hall)
            .where(Hall.id == hall_id)
            .values(**data)
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return True

    async def delete_hall(self, hall_id: int) -> bool:
        await self.get_by_id(hall_id)

        sessions_count_stmt = select(func.count(Session.id)).where(Session.hall_id == hall_id)
        sessions_count = (await self.session.execute(sessions_count_stmt)).scalar_one()
        assert sessions_count == 0, "Нельзя удалить зал, пока у него есть сеансы"

        stmt = delete(Hall).where(Hall.id == hall_id)
        await self.session.execute(stmt)
        await self.session.commit()
        return True
