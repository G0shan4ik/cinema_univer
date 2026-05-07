import enum
from datetime import date, datetime
from typing import Optional

import re

import bcrypt
from sqlalchemy import BigInteger, Enum, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, validates

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
    secret_question: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    secret_answer_hash: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(default=True)

    @hybrid_property
    def password(self):
        raise AttributeError('Пароль не доступен для чтения')

    @password.setter
    def password(self, password):
        self.set_password(password)

    def set_password(self, password: str) -> None:
        if not password:
            raise ValueError('Пароль не может быть пустым')

        if len(password) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')

        if not re.search(r'[A-Z]', password):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')

        if not re.search(r'[a-z]', password):
            raise ValueError('Пароль должен содержать хотя бы одну строчную букву')

        if not re.search(r'[0-9!@#$%^&*()]', password):
            raise ValueError('Пароль должен содержать хотя бы одну цифру или специальный символ')

        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, simple_password: str, hashed_password: Optional[str] = None) -> bool:
        actual_hash = hashed_password or self.password_hash
        if not actual_hash:
            return False
        return bcrypt.checkpw(simple_password.encode('utf-8'), actual_hash.encode('utf-8'))

    @validates('password_hash')
    def validate_password_hash(self, key, password_hash: str) -> str | None:
        if len(password_hash) != 60:
            raise ValueError('Некорректный хеш пароля')
        return password_hash

    def set_keyword(self, keyword: str):
        self.keyword_hash = bcrypt.hashpw(keyword.encode(), bcrypt.gensalt()).decode()

    def check_keyword(self, keyword: str) -> bool:
        if not self.keyword_hash:
            return False
        return bcrypt.checkpw(keyword.encode(), self.keyword_hash.encode())

    def set_secret_answer(self, question: str, answer: str):
        if not question or not question.strip():
            raise ValueError('Секретный вопрос не может быть пустым')
        if not answer or not answer.strip():
            raise ValueError('Ответ на секретный вопрос не может быть пустым')

        self.secret_question = question.strip()
        self.secret_answer_hash = bcrypt.hashpw(answer.strip().encode(), bcrypt.gensalt()).decode()

    def check_secret_answer(self, question: str, answer: str) -> bool:
        if not self.secret_question or not self.secret_answer_hash:
            return False
        return (
            self.secret_question == question.strip()
            and bcrypt.checkpw(answer.strip().encode(), self.secret_answer_hash.encode())
        )


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
