from fastapi.testclient import TestClient
from test_auth import client

from app.main import app


def test_installments_invoices_limit_and_payment() -> None:
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
            "name": "Pagamento",
            "institution": "Finora",
            "type": "checking",
            "balance": "1000.00",
        },
    )
    card = client.post(
        "/api/v1/cards",
        json={
            "name": "Finora Lime",
            "last_four": "4242",
            "credit_limit": "1000.00",
            "closing_day": 20,
            "due_day": 10,
            "color": "#B7FF2A",
        },
    )
    assert card.status_code == 201
    card_id = card.json()["id"]
    purchase = client.post(
        f"/api/v1/cards/{card_id}/purchases",
        json={
            "description": "Notebook",
            "total_amount": "300.00",
            "installment_count": 3,
            "purchase_date": "2026-08-10",
        },
    )
    assert purchase.status_code == 201
    invoices = client.get("/api/v1/invoices", params={"card_id": card_id}).json()
    assert len(invoices) == 3
    assert sum(float(item["total"]) for item in invoices) == 300.0
    assert all(item["installments"][0]["amount"] == "100.00" for item in invoices)
    updated_card = client.get("/api/v1/cards").json()[0]
    assert updated_card["used_limit"] == "300.00"
    assert updated_card["available_limit"] == "700.00"

    first = sorted(invoices, key=lambda item: item["due_date"])[0]
    closed = client.post(f"/api/v1/invoices/{first['id']}/close")
    assert closed.status_code == 200
    paid = client.post(
        f"/api/v1/invoices/{first['id']}/pay", json={"account_id": account.json()["id"]}
    )
    assert paid.status_code == 200
    assert paid.json()["status"] == "paid"
    assert client.get("/api/v1/accounts").json()[-1]["balance"] == "900.00"
    assert client.get("/api/v1/cards").json()[0]["used_limit"] == "200.00"


def test_purchase_above_limit_is_rejected() -> None:
    card_id = client.get("/api/v1/cards").json()[0]["id"]
    response = client.post(
        f"/api/v1/cards/{card_id}/purchases",
        json={
            "description": "Compra impossível",
            "total_amount": "900.00",
            "installment_count": 1,
            "purchase_date": "2026-08-18",
        },
    )
    assert response.status_code == 422


def test_cards_are_isolated_by_user() -> None:
    other = TestClient(app)
    registered = other.post(
        "/api/v1/auth/register",
        json={
            "name": "Usuário cartão",
            "email": "card-user@example.com",
            "password": "senha-segura-cartao",
        },
    )
    assert registered.status_code == 201
    assert other.get("/api/v1/cards").json() == []
    assert other.get("/api/v1/invoices").json() == []
