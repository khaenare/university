from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import create_app
from app.models import Publication, User
from app.security import hash_password


@pytest.fixture()
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add_all([
        User(username="admin", password_hash=hash_password("password"), role="admin"),
        User(username="reader", password_hash=hash_password("password"), role="reader"),
        Publication(title="Наука і життя", publisher="Українська преса", period_months=1, price=Decimal("120.00")),
    ])
    db.commit()
    db.close()

    app = create_app()

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def token(client, username):
    response = client.post("/api/auth/login", json={"username": username, "password": "password"})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_login_and_list_publications(client):
    access_token = token(client, "reader")

    response = client.get("/api/publications", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json()[0]["title"] == "Наука і життя"


def test_protected_endpoint_requires_token(client):
    response = client.get("/api/publications")

    assert response.status_code == 403


def test_reader_cannot_create_publication(client):
    access_token = token(client, "reader")

    response = client.post(
        "/api/publications",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"title": "Новини", "publisher": "Press", "period_months": 1, "price": "10.00"},
    )

    assert response.status_code == 403


def test_admin_creates_publication(client):
    access_token = token(client, "admin")
    response = client.post(
        "/api/publications",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"title": "Новини", "publisher": "Press", "period_months": 1, "price": "10.00"},
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Новини"


def test_admin_updates_and_deletes_publication(client):
    access_token = token(client, "admin")
    headers = {"Authorization": f"Bearer {access_token}"}

    update_response = client.put(
        "/api/publications/1",
        headers=headers,
        json={"title": "Оновлена назва", "publisher": "Press", "period_months": 1, "price": "125.00"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Оновлена назва"

    delete_response = client.delete("/api/publications/1", headers=headers)
    assert delete_response.status_code == 204


def test_reader_creates_subscription_and_payment(client):
    access_token = token(client, "reader")
    headers = {"Authorization": f"Bearer {access_token}"}

    subscription_response = client.post("/api/subscriptions", headers=headers, json={"publication_id": 1, "months": 2})
    assert subscription_response.status_code == 201
    subscription = subscription_response.json()
    assert subscription["total_amount"] == "240.00"

    payment_response = client.post(f"/api/subscriptions/{subscription['id']}/payments", headers=headers, json={"amount": "240.00"})
    assert payment_response.status_code == 201
    assert payment_response.json()["status"] == "registered"


def test_reader_updates_subscription_and_payment_status_then_deletes_payment(client):
    access_token = token(client, "reader")
    headers = {"Authorization": f"Bearer {access_token}"}
    subscription = client.post("/api/subscriptions", headers=headers, json={"publication_id": 1, "months": 2}).json()
    payment = client.post(f"/api/subscriptions/{subscription['id']}/payments", headers=headers, json={"amount": "240.00"}).json()

    subscription_response = client.put(f"/api/subscriptions/{subscription['id']}", headers=headers, json={"months": 3})
    assert subscription_response.status_code == 200
    assert subscription_response.json()["months"] == 3
    assert subscription_response.json()["total_amount"] == "360.00"

    payment_response = client.put(f"/api/payments/{payment['id']}", headers=headers, json={"status": "paid"})
    assert payment_response.status_code == 200
    assert payment_response.json()["status"] == "paid"

    delete_response = client.delete(f"/api/payments/{payment['id']}", headers=headers)
    assert delete_response.status_code == 204


def test_missing_subscription_returns_404(client):
    access_token = token(client, "reader")
    response = client.get("/api/subscriptions/404/payments", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 404


def test_missing_publication_for_subscription_returns_404(client):
    access_token = token(client, "reader")
    response = client.post(
        "/api/subscriptions",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"publication_id": 404, "months": 1},
    )

    assert response.status_code == 404
