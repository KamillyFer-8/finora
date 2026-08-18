from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.db.base import Base
from app.db.session import get_db
from app.main import app

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSession = sessionmaker(bind=engine, expire_on_commit=False)
Base.metadata.create_all(engine)


def override_db() -> Generator[Session, None, None]:
    with TestingSession() as session:
        yield session


app.dependency_overrides[get_db] = override_db
client = TestClient(app)


def test_complete_authentication_flow() -> None:
    credentials = {
        "name": "Kamilly",
        "email": "kamilly@example.com",
        "password": "uma-senha-segura",
    }
    registered = client.post("/api/v1/auth/register", json=credentials)
    assert registered.status_code == 201
    assert registered.json()["user"]["email"] == credentials["email"]
    assert "access_token" in registered.cookies
    assert client.get("/api/v1/auth/me").status_code == 200

    refreshed = client.post("/api/v1/auth/refresh")
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"] != registered.json()["access_token"]

    forgot = client.post("/api/v1/auth/forgot-password", json={"email": credentials["email"]})
    reset_token = forgot.json()["reset_token"]
    assert reset_token
    reset = client.post(
        "/api/v1/auth/reset-password",
        json={"token": reset_token, "new_password": "senha-nova-segura"},
    )
    assert reset.status_code == 200

    assert (
        client.post(
            "/api/v1/auth/login",
            json={"email": credentials["email"], "password": credentials["password"]},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/v1/auth/login",
            json={"email": credentials["email"], "password": "senha-nova-segura"},
        ).status_code
        == 200
    )
    assert client.post("/api/v1/auth/logout").status_code == 200
    assert client.get("/api/v1/auth/me").status_code == 401


def test_duplicate_email_is_rejected() -> None:
    payload = {
        "name": "Outra pessoa",
        "email": "kamilly@example.com",
        "password": "outra-senha-segura",
    }
    assert client.post("/api/v1/auth/register", json=payload).status_code == 409


def test_forgot_password_does_not_reveal_unknown_email() -> None:
    response = client.post("/api/v1/auth/forgot-password", json={"email": "unknown@example.com"})
    assert response.status_code == 200
    assert response.json()["reset_token"] is None
