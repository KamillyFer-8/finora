from fastapi.testclient import TestClient
from test_auth import client

from app.main import app


def test_dashboard_reports_and_csv_export() -> None:
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
            "name": "Relatórios",
            "institution": "Finora",
            "type": "checking",
            "balance": "1000.00",
        },
    ).json()
    income_category = client.post(
        "/api/v1/categories",
        json={"name": "Salário", "type": "income", "color": "#B7FF2A", "icon": "briefcase"},
    ).json()
    expense_category = client.post(
        "/api/v1/categories",
        json={"name": "Lazer", "type": "expense", "color": "#6BA8FF", "icon": "gamepad"},
    ).json()
    client.post(
        "/api/v1/transactions",
        json={
            "description": "Salário mensal",
            "amount": "1000.00",
            "type": "income",
            "account_id": account["id"],
            "category_id": income_category["id"],
            "date": "2026-08-15",
            "status": "completed",
        },
    )
    client.post(
        "/api/v1/transactions",
        json={
            "description": "Cinema",
            "amount": "200.00",
            "type": "expense",
            "account_id": account["id"],
            "category_id": expense_category["id"],
            "date": "2026-08-16",
            "status": "completed",
        },
    )

    response = client.get(
        "/api/v1/reports/dashboard", params={"start_date": "2026-08-01", "end_date": "2026-08-31"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["income"]["value"] == "1000.00"
    assert float(data["expenses"]["value"]) >= 200
    assert data["cash_flow"]
    assert any(item["name"] == "Lazer" for item in data["categories"])
    assert any(item["description"] == "Cinema" for item in data["recent_transactions"])

    exported = client.get(
        "/api/v1/reports/export.csv", params={"start_date": "2026-08-01", "end_date": "2026-08-31"}
    )
    assert exported.status_code == 200
    assert "text/csv" in exported.headers["content-type"]
    assert "Salário mensal" in exported.text
    assert "Cinema" in exported.text


def test_reports_are_isolated_and_period_is_validated() -> None:
    other = TestClient(app)
    assert (
        other.post(
            "/api/v1/auth/register",
            json={
                "name": "Analista",
                "email": "reports@example.com",
                "password": "senha-segura-reports",
            },
        ).status_code
        == 201
    )
    data = other.get(
        "/api/v1/reports/dashboard", params={"start_date": "2026-08-01", "end_date": "2026-08-31"}
    ).json()
    assert data["income"]["value"] == "0"
    assert data["recent_transactions"] == []
    invalid = other.get(
        "/api/v1/reports/dashboard", params={"start_date": "2026-09-01", "end_date": "2026-08-01"}
    )
    assert invalid.status_code == 422
