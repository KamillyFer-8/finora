import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.auth import PasswordResetToken, RefreshToken, User


class AuthRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_user_by_email(self, email: str) -> User | None:
        return self.session.scalar(select(User).where(User.email == email.lower()))

    def get_user(self, user_id: uuid.UUID) -> User | None:
        return self.session.get(User, user_id)

    def create_user(self, name: str, email: str, password_hash: str) -> User:
        user = User(name=name.strip(), email=email.lower(), password_hash=password_hash)
        self.session.add(user)
        self.session.flush()
        return user

    def save_refresh_token(
        self, user_id: uuid.UUID, jti: str, token_hash: str, expires_at: datetime
    ) -> None:
        self.session.add(
            RefreshToken(user_id=user_id, jti=jti, token_hash=token_hash, expires_at=expires_at)
        )

    def get_refresh_token(self, token_hash: str) -> RefreshToken | None:
        return self.session.scalar(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )

    def revoke_refresh_token(self, token: RefreshToken) -> None:
        token.revoked_at = datetime.now(UTC)

    def revoke_all_refresh_tokens(self, user_id: uuid.UUID) -> None:
        self.session.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=datetime.now(UTC))
        )

    def create_password_reset(
        self, user_id: uuid.UUID, token_hash: str, expires_at: datetime
    ) -> None:
        self.session.add(
            PasswordResetToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        )

    def get_password_reset(self, token_hash: str) -> PasswordResetToken | None:
        return self.session.scalar(
            select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
        )

    def commit(self) -> None:
        self.session.commit()
