from fastapi.testclient import TestClient
from test_auth import client

from app.main import app


def test_account_category_and_transaction_crud() -> None:
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "kamilly@example.com", "password": "senha-nova-segura"},
    )
    assert login.status_code == 200
    account = client.post(
        "/api/v1/accounts",
        json={
            "name": "Conta principal",
            "institution": "Finora",
            "type": "checking",
            "balance": "1000.00",
        },
    )
    assert account.status_code == 201
    account_id = account.json()["id"]
    category = client.post(
        "/api/v1/categories",
        json={"name": "Alimentação", "type": "expense", "color": "#FFB547", "icon": "utensils"},
    )
    assert category.status_code == 201
    transaction = client.post(
        "/api/v1/transactions",
        json={
            "description": "Mercado",
            "amount": "120.50",
            "type": "expense",
            "account_id": account_id,
            "category_id": category.json()["id"],
            "date": "2026-08-18",
            "status": "completed",
        },
    )
    assert transaction.status_code == 201
    transaction_id = transaction.json()["id"]
    balances = {item["id"]: item["balance"] for item in client.get("/api/v1/accounts").json()}
    assert balances[account_id] == "879.50"

    filtered = client.get("/api/v1/transactions", params={"search": "Mercado", "type": "expense"})
    assert filtered.json()["total"] == 1
    updated = client.patch(f"/api/v1/transactions/{transaction_id}", json={"amount": "100.00"})
    assert updated.status_code == 200
    balances = {item["id"]: item["balance"] for item in client.get("/api/v1/accounts").json()}
    assert balances[account_id] == "900.00"

    copied = client.post(f"/api/v1/transactions/{transaction_id}/duplicate")
    assert copied.status_code == 201
    balances = {item["id"]: item["balance"] for item in client.get("/api/v1/accounts").json()}
    assert balances[account_id] == "800.00"
    assert client.delete(f"/api/v1/transactions/{transaction_id}").status_code == 204
    balances = {item["id"]: item["balance"] for item in client.get("/api/v1/accounts").json()}
    assert balances[account_id] == "900.00"


def test_financial_data_is_isolated_by_user() -> None:
    other = TestClient(app)
    registered = other.post(
        "/api/v1/auth/register",
        json={
            "name": "Outro usuário",
            "email": "other@example.com",
            "password": "senha-segura-outro",
        },
    )
    assert registered.status_code == 201
    assert other.get("/api/v1/accounts").json() == []
    assert other.get("/api/v1/transactions").json()["total"] == 0


def test_recurrence_lifecycle() -> None:
    client.post(
        "/api/v1/auth/login",
        json={"email": "kamilly@example.com", "password": "senha-nova-segura"},
    )
    account = client.post(
        "/api/v1/accounts",
        json={
            "name": "Recorrências",
            "institution": "Finora",
            "type": "checking",
            "balance": "0",
        },
    ).json()
    created = client.post(
        "/api/v1/recurrences",
        json={
            "description": "Academia",
            "amount": "99.90",
            "type": "expense",
            "account_id": account["id"],
            "frequency": "monthly",
            "next_run_at": "2026-09-01",
        },
    )
    assert created.status_code == 201
    assert client.get("/api/v1/recurrences").json()[0]["description"] == "Academia"
    assert client.delete(f"/api/v1/recurrences/{created.json()['id']}").status_code == 204
    assert client.get("/api/v1/recurrences").json() == []
