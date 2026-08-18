import secrets
import uuid
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import create_token, decode_token, hash_password, hash_token, verify_password
from app.models.auth import User
from app.repositories.auth import AuthRepository


class AuthService:
    def __init__(self, repository: AuthRepository) -> None:
        self.repository = repository

    def register(self, name: str, email: str, password: str) -> tuple[User, str, str]:
        if self.repository.get_user_by_email(email):
            raise HTTPException(status.HTTP_409_CONFLICT, "Este e-mail já está cadastrado")
        user = self.repository.create_user(name, email, hash_password(password))
        access, refresh = self._issue_session(user)
        self.repository.commit()
        return user, access, refresh

    def login(self, email: str, password: str) -> tuple[User, str, str]:
        user = self.repository.get_user_by_email(email)
        if not user or not verify_password(password, user.password_hash) or not user.is_active:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "E-mail ou senha inválidos")
        access, refresh = self._issue_session(user)
        self.repository.commit()
        return user, access, refresh

    def refresh(self, raw_token: str) -> tuple[User, str, str]:
        try:
            payload = decode_token(raw_token, "refresh")
        except jwt.InvalidTokenError as error:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sessão inválida") from error
        stored = self.repository.get_refresh_token(hash_token(raw_token))
        if not stored or stored.revoked_at or self._expired(stored.expires_at):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sessão expirada")
        self.repository.revoke_refresh_token(stored)
        user = self.repository.get_user(uuid.UUID(payload["sub"]))
        if not user or not user.is_active:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuário indisponível")
        access, refresh = self._issue_session(user)
        self.repository.commit()
        return user, access, refresh

    def logout(self, raw_token: str | None) -> None:
        if raw_token and (stored := self.repository.get_refresh_token(hash_token(raw_token))):
            if not stored.revoked_at:
                self.repository.revoke_refresh_token(stored)
                self.repository.commit()

    def forgot_password(self, email: str) -> str | None:
        user = self.repository.get_user_by_email(email)
        if not user:
            return None
        raw_token = secrets.token_urlsafe(48)
        expires_at = datetime.now(UTC) + timedelta(minutes=settings.password_reset_minutes)
        self.repository.create_password_reset(user.id, hash_token(raw_token), expires_at)
        self.repository.commit()
        return raw_token

    def reset_password(self, raw_token: str, new_password: str) -> None:
        reset = self.repository.get_password_reset(hash_token(raw_token))
        if not reset or reset.used_at or self._expired(reset.expires_at):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Token inválido ou expirado")
        user = self.repository.get_user(reset.user_id)
        if not user:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Token inválido")
        user.password_hash = hash_password(new_password)
        reset.used_at = datetime.now(UTC)
        self.repository.revoke_all_refresh_tokens(user.id)
        self.repository.commit()

    def _issue_session(self, user: User) -> tuple[str, str]:
        access, _, _ = create_token(
            user.id, "access", timedelta(minutes=settings.access_token_minutes)
        )
        refresh, jti, expires_at = create_token(
            user.id, "refresh", timedelta(days=settings.refresh_token_days)
        )
        self.repository.save_refresh_token(user.id, jti, hash_token(refresh), expires_at)
        return access, refresh

    @staticmethod
    def _expired(value: datetime) -> bool:
        aware = value if value.tzinfo else value.replace(tzinfo=UTC)
        return aware <= datetime.now(UTC)
