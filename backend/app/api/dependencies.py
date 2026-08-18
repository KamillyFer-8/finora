import uuid
from typing import Annotated

import jwt
from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models.auth import User
from app.repositories.auth import AuthRepository

SessionDep = Annotated[Session, Depends(get_db)]


def get_current_user(
    session: SessionDep, access_token: Annotated[str | None, Cookie()] = None
) -> User:
    if not access_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Autenticação necessária")
    try:
        payload = decode_token(access_token, "access")
        user_id = uuid.UUID(payload["sub"])
    except (jwt.InvalidTokenError, ValueError, KeyError) as error:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sessão inválida") from error
    user = AuthRepository(session).get_user(user_id)
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuário indisponível")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
