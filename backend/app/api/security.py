from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from os import getenv
from secrets import token_urlsafe

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_session
from app.database.models import User, UserRole


ACCESS_TOKEN_TTL_MINUTES = int(getenv("ACCESS_TOKEN_TTL_MINUTES", "20"))
REFRESH_TOKEN_TTL_HOURS = int(getenv("REFRESH_TOKEN_TTL_HOURS", "8"))


@dataclass
class AccessTokenData:
    token: str
    user_id: int
    expires_at: datetime


@dataclass
class RefreshTokenData:
    token: str
    user_id: int
    expires_at: datetime


class SessionManager:
    def __init__(self):
        self.access_tokens: dict[str, AccessTokenData] = {}
        self.refresh_tokens: dict[str, RefreshTokenData] = {}

    @staticmethod
    def _utcnow() -> datetime:
        return datetime.now(timezone.utc)

    def _cleanup(self):
        now = self._utcnow()

        expired_access_tokens = [
            token for token, data in self.access_tokens.items()
            if data.expires_at <= now
        ]
        for token in expired_access_tokens:
            self.access_tokens.pop(token, None)

        expired_refresh_tokens = [
            token for token, data in self.refresh_tokens.items()
            if data.expires_at <= now
        ]
        for token in expired_refresh_tokens:
            self.refresh_tokens.pop(token, None)

    def issue_tokens(self, user_id: int) -> tuple[AccessTokenData, RefreshTokenData]:
        self._cleanup()
        now = self._utcnow()

        access = AccessTokenData(
            token=token_urlsafe(32),
            user_id=user_id,
            expires_at=now + timedelta(minutes=ACCESS_TOKEN_TTL_MINUTES),
        )
        refresh = RefreshTokenData(
            token=token_urlsafe(48),
            user_id=user_id,
            expires_at=now + timedelta(hours=REFRESH_TOKEN_TTL_HOURS),
        )

        self.access_tokens[access.token] = access
        self.refresh_tokens[refresh.token] = refresh
        return access, refresh

    def refresh_access_token(self, refresh_token: str) -> tuple[AccessTokenData, RefreshTokenData]:
        self._cleanup()
        refresh = self.refresh_tokens.get(refresh_token)
        if refresh is None or refresh.expires_at <= self._utcnow():
            self.refresh_tokens.pop(refresh_token, None)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Сессия истекла. Выполните вход заново.",
            )

        access = AccessTokenData(
            token=token_urlsafe(32),
            user_id=refresh.user_id,
            expires_at=self._utcnow() + timedelta(minutes=ACCESS_TOKEN_TTL_MINUTES),
        )
        self.access_tokens[access.token] = access
        return access, refresh

    def get_access_token(self, token: str) -> AccessTokenData:
        self._cleanup()
        access = self.access_tokens.get(token)
        if access is None or access.expires_at <= self._utcnow():
            self.access_tokens.pop(token, None)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Срок действия сессии истек. Обновите вход.",
            )
        return access

    def revoke_access_token(self, token: str | None):
        if token:
            self.access_tokens.pop(token, None)

    def revoke_refresh_token(self, token: str | None):
        if token:
            self.refresh_tokens.pop(token, None)

    def revoke_user_sessions(self, user_id: int):
        access_tokens = [
            token for token, data in self.access_tokens.items()
            if data.user_id == user_id
        ]
        for token in access_tokens:
            self.access_tokens.pop(token, None)

        refresh_tokens = [
            token for token, data in self.refresh_tokens.items()
            if data.user_id == user_id
        ]
        for token in refresh_tokens:
            self.refresh_tokens.pop(token, None)


session_manager = SessionManager()


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация.",
        )

    auth_type, _, token = authorization.partition(" ")
    if auth_type.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректный токен авторизации.",
        )

    return token


async def get_current_user(
    authorization: str | None = Header(default=None),
    session: AsyncSession = Depends(get_session),
) -> User:
    token = _extract_bearer_token(authorization)
    token_data = session_manager.get_access_token(token)

    stmt = select(User).where(User.id == token_data.user_id)
    user = (await session.execute(stmt)).scalar_one_or_none()

    if user is None or not user.is_active:
        session_manager.revoke_user_sessions(token_data.user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь недоступен. Выполните вход заново.",
        )

    return user


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ только для администратора.",
        )
    return current_user


def require_same_user_or_admin(current_user: User, user_id: int):
    if current_user.role == UserRole.ADMIN:
        return

    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для этого действия.",
        )
