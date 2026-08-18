from typing import Annotated

from fastapi import APIRouter, Cookie, HTTPException, Response, status

from app.api.dependencies import CurrentUser, SessionDep
from app.core.config import settings
from app.repositories.auth import AuthRepository
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
    UserResponse,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def set_session_cookies(response: Response, access: str, refresh: str) -> None:
    response.set_cookie(
        "access_token",
        access,
        max_age=settings.access_token_minutes * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        "refresh_token",
        refresh,
        max_age=settings.refresh_token_days * 86400,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


def auth_response(response: Response, user: object, access: str, refresh: str) -> AuthResponse:
    set_session_cookies(response, access, refresh)
    return AuthResponse(access_token=access, user=UserResponse.model_validate(user))


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, response: Response, session: SessionDep) -> AuthResponse:
    user, access, refresh = AuthService(AuthRepository(session)).register(
        payload.name, payload.email, payload.password
    )
    return auth_response(response, user, access, refresh)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, response: Response, session: SessionDep) -> AuthResponse:
    user, access, refresh = AuthService(AuthRepository(session)).login(
        payload.email, payload.password
    )
    return auth_response(response, user, access, refresh)


@router.post("/refresh", response_model=AuthResponse)
def refresh(
    response: Response, session: SessionDep, refresh_token: Annotated[str | None, Cookie()] = None
) -> AuthResponse:
    if not refresh_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token ausente")
    user, access, new_refresh = AuthService(AuthRepository(session)).refresh(refresh_token)
    return auth_response(response, user, access, new_refresh)


@router.post("/logout", response_model=MessageResponse)
def logout(
    response: Response, session: SessionDep, refresh_token: Annotated[str | None, Cookie()] = None
) -> MessageResponse:
    AuthService(AuthRepository(session)).logout(refresh_token)
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return MessageResponse(message="Sessão encerrada")


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(payload: ForgotPasswordRequest, session: SessionDep) -> ForgotPasswordResponse:
    token = AuthService(AuthRepository(session)).forgot_password(payload.email)
    return ForgotPasswordResponse(
        message="Se o e-mail existir, as instruções serão enviadas.",
        reset_token=token if settings.environment == "development" else None,
    )


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, session: SessionDep) -> MessageResponse:
    AuthService(AuthRepository(session)).reset_password(payload.token, payload.new_password)
    return MessageResponse(message="Senha redefinida com sucesso")


@router.get("/me", response_model=UserResponse)
def me(current_user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(current_user)
