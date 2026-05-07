from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from os import getenv

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.database import get_session
from backend.database.models import User, UserRole


ACCESS_TOKEN_TTL_MINUTES = int(getenv("ACCESS_TOKEN_TTL_MINUTES", "20"))
REFRESH_TOKEN_TTL_HOURS = int(getenv("REFRESH_TOKEN_TTL_HOURS", "8"))
JWT_SECRET = getenv("JWT_SECRET", "cinemahub-dev-secret")
JWT_ALGORITHM = "HS256"


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
        self.revoked_access_tokens: set[str] = set()
        self.revoked_refresh_tokens: set[str] = set()
        self.revoked_users_after: dict[int, datetime] = {}

    @staticmethod
    def _utcnow() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _b64url_encode(value: bytes) -> str:
        return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")

    @staticmethod
    def _b64url_decode(value: str) -> bytes:
        padding = "=" * (-len(value) % 4)
        return base64.urlsafe_b64decode(f"{value}{padding}")

    def _encode_jwt(self, payload: dict) -> str:
        header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
        encoded_header = self._b64url_encode(
            json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
        )
        encoded_payload = self._b64url_encode(
            json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        )
        signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
        signature = hmac.new(JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()
        return f"{encoded_header}.{encoded_payload}.{self._b64url_encode(signature)}"

    def _decode_jwt(self, token: str, expected_type: str) -> dict:
        try:
            encoded_header, encoded_payload, encoded_signature = token.split(".")
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Некорректный токен авторизации.",
            ) from exc

        signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
        try:
            actual_signature = self._b64url_decode(encoded_signature)
            expected_signature = hmac.new(
                JWT_SECRET.encode("utf-8"),
                signing_input,
                hashlib.sha256,
            ).digest()
        except (ValueError, binascii.Error) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Некорректный формат токена.",
            ) from exc

        if not hmac.compare_digest(actual_signature, expected_signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Некорректная подпись токена.",
            )

        try:
            payload = json.loads(self._b64url_decode(encoded_payload).decode("utf-8"))
        except (ValueError, binascii.Error, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Не удалось прочитать токен.",
            ) from exc

        if "exp" not in payload or "iat" not in payload or "sub" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен не содержит обязательные поля.",
            )

        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        if expires_at <= self._utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Срок действия сессии истек. Обновите вход.",
            )

        if payload.get("type") != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Некорректный тип токена.",
            )

        return payload

    def _build_token_data(self, user_id: int, token_type: str, ttl: timedelta):
        now = self._utcnow()
        expires_at = now + ttl
        payload = {
            "sub": str(user_id),
            "type": token_type,
            "iat": int(now.timestamp()),
            "exp": int(expires_at.timestamp()),
        }
        token = self._encode_jwt(payload)

        token_data_cls = AccessTokenData if token_type == "access" else RefreshTokenData
        return token_data_cls(token=token, user_id=user_id, expires_at=expires_at)

    def issue_tokens(self, user_id: int) -> tuple[AccessTokenData, RefreshTokenData]:
        access = self._build_token_data(
            user_id=user_id,
            token_type="access",
            ttl=timedelta(minutes=ACCESS_TOKEN_TTL_MINUTES),
        )
        refresh = self._build_token_data(
            user_id=user_id,
            token_type="refresh",
            ttl=timedelta(hours=REFRESH_TOKEN_TTL_HOURS),
        )
        return access, refresh

    def refresh_access_token(self, refresh_token: str) -> tuple[AccessTokenData, RefreshTokenData]:
        if refresh_token in self.revoked_refresh_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Сессия истекла. Выполните вход заново.",
            )
        payload = self._decode_jwt(refresh_token, expected_type="refresh")
        user_id = int(payload["sub"])
        revoked_after = self.revoked_users_after.get(user_id)
        issued_at = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        if revoked_after and issued_at <= revoked_after:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Сессия истекла. Выполните вход заново.",
            )

        self.revoked_refresh_tokens.add(refresh_token)
        access = self._build_token_data(
            user_id=user_id,
            token_type="access",
            ttl=timedelta(minutes=ACCESS_TOKEN_TTL_MINUTES),
        )
        refresh = self._build_token_data(
            user_id=user_id,
            token_type="refresh",
            ttl=timedelta(hours=REFRESH_TOKEN_TTL_HOURS),
        )
        return access, refresh

    def get_access_token(self, token: str) -> AccessTokenData:
        if token in self.revoked_access_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Срок действия сессии истек. Обновите вход.",
            )
        payload = self._decode_jwt(token, expected_type="access")
        user_id = int(payload["sub"])
        issued_at = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        revoked_after = self.revoked_users_after.get(user_id)
        if revoked_after and issued_at <= revoked_after:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Срок действия сессии истек. Обновите вход.",
            )
        return AccessTokenData(
            token=token,
            user_id=user_id,
            expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        )

    def revoke_access_token(self, token: str | None):
        if token:
            self.revoked_access_tokens.add(token)

    def revoke_refresh_token(self, token: str | None):
        if token:
            self.revoked_refresh_tokens.add(token)

    def revoke_user_sessions(self, user_id: int):
        self.revoked_users_after[user_id] = self._utcnow()


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
