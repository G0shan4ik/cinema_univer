from datetime import date, datetime, timedelta

from sqlalchemy import select

from backend.database.core import session_maker
from backend.database.models import Favorite, Hall, Movie, Session, Ticket, TicketStatus, User, UserRole


async def seed_initial_data():
    async with session_maker() as session:
        movies_exist = (await session.execute(select(Movie.id).limit(1))).scalar_one_or_none()
        if movies_exist:
            return

        admin = User(
            email="admin@cinemahub.com",
            name="Cinema Admin",
            role=UserRole.ADMIN,
            is_active=True,
        )
        admin.password = "Admin123!"
        admin.set_keyword("cinema")
        admin.set_secret_answer("Любимый фильм", "Матрица")

        demo_user = User(
            email="user@cinemahub.com",
            name="Demo User",
            role=UserRole.USER,
            is_active=True,
        )
        demo_user.password = "User123!"
        demo_user.set_keyword("movies")
        demo_user.set_secret_answer("Любимый фильм", "Интерстеллар")

        halls = [
            Hall(name="Зал 1", total_rows=8, seats_per_row=10),
            Hall(name="Зал 2", total_rows=10, seats_per_row=12),
        ]

        movies = [
            Movie(
                title="Дюна: Часть вторая",
                description="Пол Атрейдес объединяется с фременами, чтобы защитить Арракис и изменить ход истории.",
                genre="Sci-Fi",
                duration_minutes=166,
                rating=8.7,
                poster_url="https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=900&q=80",
                release_date=date(2024, 3, 1),
            ),
            Movie(
                title="Фуриоса",
                description="История становления легендарной Фуриосы в мире постапокалипсиса.",
                genre="Action",
                duration_minutes=148,
                rating=8.1,
                poster_url="https://images.unsplash.com/photo-1536440136628-849c177e76a1?auto=format&fit=crop&w=900&q=80",
                release_date=date(2024, 5, 23),
            ),
            Movie(
                title="Головоломка 2",
                description="Новые эмоции приходят в команду Райли и делают подростковую жизнь еще интереснее.",
                genre="Animation",
                duration_minutes=103,
                rating=8.4,
                poster_url="https://images.unsplash.com/photo-1514306191717-452ec28c7814?auto=format&fit=crop&w=900&q=80",
                release_date=date(2024, 6, 12),
            ),

            Movie(
                title="asdfgas 2",
                description="Новые эмоции приходят в команду Райли и делают подростковую жизнь еще интереснее.",
                genre="Animation",
                duration_minutes=103,
                rating=8.4,
                poster_url="https://images.unsplash.com/photo-1514306191717-452ec28c7814?auto=format&fit=crop&w=900&q=80",
                release_date=date(2004, 6, 12),
            ),
            Movie(
                title="asdfgddd 2",
                description="Новые эмоции приходят в команду Райли и делают подростковую жизнь еще интереснее.",
                genre="Animation",
                duration_minutes=103,
                rating=8.4,
                poster_url="https://images.unsplash.com/photo-1514306191717-452ec28c7814?auto=format&fit=crop&w=900&q=80",
                release_date=date(2023, 6, 12),
            ),
            Movie(
                title="ddd 2",
                description="Новые эмоции приходят в команду Райли и делают подростковую жизнь еще интереснее.",
                genre="Animation",
                duration_minutes=103,
                rating=8.4,
                poster_url="https://images.unsplash.com/photo-1514306191717-452ec28c7814?auto=format&fit=crop&w=900&q=80",
                release_date=date(2014, 6, 11),
            ),
            Movie(
                title="ssdsdsd 2",
                description="Новые эмоции приходят в команду Райли и делают подростковую жизнь еще интереснее.",
                genre="Animation",
                duration_minutes=103,
                rating=8.4,
                poster_url="https://images.unsplash.com/photo-1514306191717-452ec28c7814?auto=format&fit=crop&w=900&q=80",
                release_date=date(2024, 6, 22),
            ),
        ]

        session.add_all([admin, demo_user, *halls, *movies])
        await session.flush()

        now = datetime.utcnow()
        sessions = [
            Session(movie_id=movies[0].id, hall_id=halls[0].id, start_time=now + timedelta(hours=6), price=18.5),
            Session(movie_id=movies[0].id, hall_id=halls[1].id, start_time=now + timedelta(days=1, hours=2), price=22.0),
            Session(movie_id=movies[1].id, hall_id=halls[1].id, start_time=now + timedelta(hours=12), price=19.0),
            Session(movie_id=movies[2].id, hall_id=halls[0].id, start_time=now + timedelta(days=1, hours=5), price=14.0),
        ]
        session.add_all(sessions)
        await session.flush()

        favorites = [
            Favorite(user_id=demo_user.id, movie_id=movies[0].id),
            Favorite(user_id=demo_user.id, movie_id=movies[2].id),
        ]
        tickets = [
            Ticket(
                user_id=demo_user.id,
                session_id=sessions[0].id,
                seat_row=3,
                seat_number=5,
                status=TicketStatus.BOOKED,
            ),
            Ticket(
                user_id=demo_user.id,
                session_id=sessions[2].id,
                seat_row=4,
                seat_number=7,
                status=TicketStatus.PAID,
            ),
        ]

        session.add_all([*favorites, *tickets])
        await session.commit()
