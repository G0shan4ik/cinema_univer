import enum
from datetime import date, datetime
from typing import Optional

import bcrypt
from sqlalchemy import BigInteger, Enum, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from .core import Base


# ---------------- ENUMS ----------------

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class TicketStatus(str, enum.Enum):
    BOOKED = "booked"
    PAID = "paid"
    CANCELLED = "cancelled"


# ---------------- USER ----------------

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(60), nullable=False)
    keyword_hash: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(default=True)

    @hybrid_property
    def password(self):
        raise AttributeError('Пароль не доступен')

    @password.setter
    def password(self, password: str):
        self.set_password(password)

    def set_password(self, password: str):
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def set_keyword(self, keyword: str):
        self.keyword_hash = bcrypt.hashpw(keyword.encode(), bcrypt.gensalt()).decode()

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

    def check_keyword(self, keyword: str) -> bool:
        if not self.keyword_hash:
            return False
        return bcrypt.checkpw(keyword.encode(), self.keyword_hash.encode())


# ---------------- MOVIE ----------------

class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    genre: Mapped[str] = mapped_column(String(100), index=True)
    duration_minutes: Mapped[int] = mapped_column(nullable=False)
    rating: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)
    poster_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    release_date: Mapped[Optional[date]] = mapped_column(nullable=True)


# ---------------- HALL ----------------

class Hall(Base):
    __tablename__ = "halls"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    total_rows: Mapped[int] = mapped_column(nullable=False)
    seats_per_row: Mapped[int] = mapped_column(nullable=False)


# ---------------- SESSION ----------------

class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), nullable=False)
    hall_id: Mapped[int] = mapped_column(ForeignKey("halls.id"), nullable=False)

    start_time: Mapped[datetime] = mapped_column(nullable=False, index=True)
    price: Mapped[float] = mapped_column(Float(), nullable=False)


# ---------------- TICKET ----------------

class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), nullable=False)

    seat_row: Mapped[int] = mapped_column(nullable=False)
    seat_number: Mapped[int] = mapped_column(nullable=False)

    status: Mapped[TicketStatus] = mapped_column(Enum(TicketStatus), default=TicketStatus.BOOKED)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("session_id", "seat_row", "seat_number", name="unique_seat"),
    )


# ---------------- FAVORITES ----------------

class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="unique_favorite"),
    )


__all__ = [
    "User", "Movie", "Session", "Hall",
    "Ticket", "Favorite",
    "UserRole", "TicketStatus"
]
