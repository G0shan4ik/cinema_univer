from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, model_validator


class BaseResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------------- BASE ----------------

class CreatedModel(BaseModel):
    created_id: int


class StatusModel(BaseModel):
    status: bool


# ---------------- ENUM ----------------

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class TicketStatus(str, Enum):
    BOOKED = "booked"
    PAID = "paid"
    CANCELLED = "cancelled"


# ---------------- AUTH / USER ----------------

class ActiveModel(BaseResponseModel):
    id: int
    email: EmailStr
    name: str
    role: UserRole
    is_active: bool


class AuthResponse(ActiveModel):
    access_token: str
    refresh_token: str
    access_expires_at: datetime
    refresh_expires_at: datetime


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    secret_question: Optional[str] = None
    secret_answer: Optional[str] = None

    @model_validator(mode="after")
    def validate_secret_pair(self):
        has_question = bool(self.secret_question and self.secret_question.strip())
        has_answer = bool(self.secret_answer and self.secret_answer.strip())

        if has_question != has_answer:
            raise ValueError("Для восстановления нужно указать и секретный вопрос, и ответ.")

        return self


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None


class UserResponse(BaseResponseModel):
    id: int
    email: EmailStr
    name: str
    created_at: datetime
    role: UserRole
    is_active: bool


class UserRequestUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None


class SetKeyword(BaseModel):
    user_id: int
    keyword: Optional[str] = None
    secret_question: Optional[str] = None
    secret_answer: Optional[str] = None

    @model_validator(mode="after")
    def validate_secret_payload(self):
        has_keyword = bool(self.keyword and self.keyword.strip())
        has_question = bool(self.secret_question and self.secret_question.strip())
        has_answer = bool(self.secret_answer and self.secret_answer.strip())

        if has_question != has_answer:
            raise ValueError("Секретный вопрос и ответ нужно передавать вместе.")

        if not has_keyword and not (has_question and has_answer):
            raise ValueError("Нужно передать ключевое слово или секретный вопрос с ответом.")

        return self


class RecoverPassword(BaseModel):
    email: EmailStr
    keyword: Optional[str] = None
    secret_question: Optional[str] = None
    secret_answer: Optional[str] = None
    new_password: str

    @model_validator(mode="after")
    def validate_recovery_payload(self):
        has_keyword = bool(self.keyword and self.keyword.strip())
        has_question = bool(self.secret_question and self.secret_question.strip())
        has_answer = bool(self.secret_answer and self.secret_answer.strip())

        if has_question != has_answer:
            raise ValueError("Для восстановления нужно указать и секретный вопрос, и ответ.")

        if not has_keyword and not (has_question and has_answer):
            raise ValueError("Укажите ключевое слово или секретный вопрос с ответом.")

        return self


# ---------------- MOVIE ----------------

class MovieCreate(BaseModel):
    title: str
    description: Optional[str] = None
    genre: str
    duration_minutes: int
    rating: Optional[float] = None
    poster_url: Optional[str] = None
    release_date: Optional[date] = None


class MovieUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    duration_minutes: Optional[int] = None
    rating: Optional[float] = None
    poster_url: Optional[str] = None
    release_date: Optional[date] = None


class MovieResponse(BaseResponseModel):
    id: int
    title: str
    description: Optional[str]
    genre: str
    duration_minutes: int
    rating: Optional[float]
    poster_url: Optional[str]
    release_date: Optional[date]


class MovieListResponse(BaseModel):
    items: list[MovieResponse]
    total: int
    limit: int
    offset: int
    has_more: bool


# ---------------- HALL ----------------

class HallCreate(BaseModel):
    name: str
    total_rows: int
    seats_per_row: int


class HallUpdate(BaseModel):
    name: Optional[str] = None
    total_rows: Optional[int] = None
    seats_per_row: Optional[int] = None


class HallResponse(BaseResponseModel):
    id: int
    name: str
    total_rows: int
    seats_per_row: int


# ---------------- SESSION ----------------

class SessionCreate(BaseModel):
    movie_id: int
    hall_id: int
    start_time: datetime
    price: float


class SessionUpdate(BaseModel):
    movie_id: Optional[int] = None
    hall_id: Optional[int] = None
    start_time: Optional[datetime] = None
    price: Optional[float] = None


class SessionResponse(BaseModel):
    id: int
    movie_id: int
    hall_id: int
    start_time: datetime
    price: float
    movie_title: Optional[str] = None
    hall_name: Optional[str] = None


class SeatResponse(BaseModel):
    seat_row: int
    seat_number: int
    status: TicketStatus


class SessionSeatsResponse(BaseModel):
    session_id: int
    hall_id: int
    total_rows: int
    seats_per_row: int
    occupied_seats: list[SeatResponse]


# ---------------- TICKET ----------------

class TicketCreate(BaseModel):
    user_id: int
    session_id: int
    seat_row: int
    seat_number: int


class TicketStatusUpdate(BaseModel):
    status: TicketStatus


class TicketResponse(BaseResponseModel):
    id: int
    user_id: int
    session_id: int
    seat_row: int
    seat_number: int
    status: TicketStatus
    created_at: datetime


class TicketDetailResponse(BaseModel):
    id: int
    user_id: int
    session_id: int
    seat_row: int
    seat_number: int
    status: TicketStatus
    created_at: datetime
    movie_id: int
    movie_title: str
    hall_id: int
    hall_name: str
    start_time: datetime
    price: float


# ---------------- FAVORITE ----------------

class FavoriteCreate(BaseModel):
    user_id: int
    movie_id: int


class FavoriteResponse(BaseResponseModel):
    id: int
    user_id: int
    movie_id: int


class FavoriteMovieResponse(BaseModel):
    favorite_id: int
    movie_id: int
    title: str
    description: Optional[str]
    genre: str
    duration_minutes: int
    rating: Optional[float]
    poster_url: Optional[str]
    release_date: Optional[date]
