from fastapi.testclient import TestClient
from test_auth import client

from app.main import app


def test_budget_alerts_and_goal_contributions() -> None:
    assert (
        client.post(
            "/api/v1/auth/login",
            json={"email": "kamilly@example.com", "password": "senha-nova-segura"},
        ).status_code
        == 200
    )
    account = client.post(
        "/api/v1/accounts",
        json={
            "name": "Planejamento",
            "institution": "Finora",
            "type": "checking",
            "balance": "2000.00",
        },
    ).json()
    category = client.post(
        "/api/v1/categories",
        json={"name": "Moradia", "type": "expense", "color": "#FFB547", "icon": "house"},
    ).json()
    transaction = client.post(
        "/api/v1/transactions",
        json={
            "description": "Aluguel",
            "amount": "850.00",
            "type": "expense",
            "account_id": account["id"],
            "category_id": category["id"],
            "date": "2026-08-10",
            "status": "completed",
        },
    ).json()
    budget = client.post(
        "/api/v1/budgets",
        json={
            "category_id": category["id"],
            "period_start": "2026-08-01",
            "period_end": "2026-08-31",
            "limit_amount": "1000.00",
        },
    )
    assert budget.status_code == 201
    assert budget.json()["percentage"] == 85.0
    assert budget.json()["alert_level"] == "warning"
    assert client.get("/api/v1/alerts").json()[0]["level"] == "warning"
    client.patch(f"/api/v1/transactions/{transaction['id']}", json={"amount": "1100.00"})
    assert client.get("/api/v1/budgets").json()[0]["alert_level"] == "exceeded"

    goal = client.post(
        "/api/v1/goals",
        json={"name": "Reserva", "target_amount": "1000.00", "deadline": "2027-08-01"},
    )
    assert goal.status_code == 201
    contribution = client.post(
        f"/api/v1/goals/{goal.json()['id']}/contributions",
        json={"account_id": account["id"], "amount": "500.00", "contributed_at": "2026-08-18"},
    )
    assert contribution.status_code == 201
    updated_goal = client.get("/api/v1/goals").json()[0]
    assert updated_goal["current_amount"] == "500.00"
    assert updated_goal["percentage"] == 50.0
    balances = {item["id"]: item["balance"] for item in client.get("/api/v1/accounts").json()}
    assert balances[account["id"]] == "400.00"
    assert (
        client.delete(f"/api/v1/goals/contributions/{contribution.json()['id']}").status_code == 204
    )
    balances = {item["id"]: item["balance"] for item in client.get("/api/v1/accounts").json()}
    assert balances[account["id"]] == "900.00"


def test_planning_is_isolated_by_user() -> None:
    other = TestClient(app)
    response = other.post(
        "/api/v1/auth/register",
        json={
            "name": "Planejador",
            "email": "planning@example.com",
            "password": "senha-segura-planning",
        },
    )
    assert response.status_code == 201
    assert other.get("/api/v1/budgets").json() == []
    assert other.get("/api/v1/goals").json() == []
    assert other.get("/api/v1/alerts").json() == []
