from .include import (
    User, UserRole,
    select, update, insert,
    BaseDatabaseDep,
    Optional
)


class UserService(BaseDatabaseDep):
    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(
            User.email == email
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def create_user(self, email: str, name: str, password: str) -> int:
        temp_user = User()
        temp_user.password = password
        password_hash = temp_user.password_hash

        result = await self.get_by_email(email)
        assert not result, 'Пользователь уже существует!'

        stmt = insert(User).values(
            email=email,
            name=name,
            password_hash=password_hash,
            role=UserRole.USER,
            is_active=True
        ).returning(User.id)

        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar()

    async def sign_in(self, email: str, password: str) -> Optional[dict]:
        result = await self.get_by_email(email)
        assert result, 'Пользователь не найден!'

        check_valid_pass = result.check_password(password)
        assert check_valid_pass, 'Неверный пароль!'

        assert result.is_active, 'Аккаунт деактивирован!'

        return {
            'id': result.id,
            'email': result.email,
            'name': result.name,
            'role': result.role.value,
            'is_active': result.is_active
        }

    async def get_by_id(self, user_id: int) -> Optional[User]:
        stmt = select(User).where(
            User.id == user_id
        )
        result = (await self.session.execute(stmt)).scalar_one_or_none()

        assert result, f'Пользователь с ID == {user_id} не найден!'
        return result

    async def deactivate_user(self, user_id: int) -> bool:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(is_active=False)
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return True

    async def update_user(self, user_id: int, data: dict) -> bool:
        result = await self.get_by_id(user_id)

        if result:
            allowed_fields = {
                "email",
                "name"
            }

            update_data = {k: v for k, v in data.items() if k in allowed_fields}
            assert update_data, "Нет полей для обновления"

            if "email" in update_data and update_data["email"] != result.email:
                user_with_email = await self.get_by_email(update_data["email"])
                assert not user_with_email, "Пользователь с таким email уже существует"

            stmt = (
                update(User)
                .where(User.id == user_id)
                .values(**update_data)
            )
            await self.session.execute(stmt)
            await self.session.commit()

            return True

        raise ValueError('Пользователь не найден!')

    async def set_keyword(self, user_id: int, keyword: str) -> bool:
        user = await self.get_by_id(user_id)

        user.set_keyword(keyword)

        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(keyword_hash=user.keyword_hash)
        )
        await self.session.execute(stmt)
        await self.session.commit()

        return True

    async def recover_password(self, email: str, keyword: str, new_password: str) -> bool:
        user = await self.get_by_email(email)

        assert user, 'Пользователь не найден!'
        assert user.check_keyword(keyword), 'Неверное ключевое слово!'

        temp_user = User()
        temp_user.password = new_password

        stmt = (
            update(User)
            .where(User.id == user.id)
            .values(password_hash=temp_user.password_hash)
        )
        await self.session.execute(stmt)
        await self.session.commit()

        return True

    async def get_all(self, page: int = 1, per_page: int = 10) -> list[User]:
        offset = (page - 1) * per_page

        stmt = (
            select(User)
            .offset(offset)
            .limit(per_page)
        )
        result = await self.session.execute(stmt)

        return result.scalars().all()
