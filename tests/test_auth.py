import uuid
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_register_user():
    payload = {
        "email": f"test_auth_user_{uuid.uuid4().hex}@example.com",
        "password": "TestPassword123"
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code in [200, 201, 400]

    if response.status_code in [200, 201]:
        data = response.json()
        assert data["email"] == payload["email"]


def test_login_user():
    register_payload = {
        "email": "test_login_user@example.com",
        "password": "TestPassword123"
    }

    client.post("/auth/register", json=register_payload)

    login_payload = {
        "username": register_payload["email"],
        "password": register_payload["password"]
    }

    response = client.post("/auth/login", data=login_payload)

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_get_me_requires_auth():
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_get_me_with_token():
    register_payload = {
        "email": "test_me_user@example.com",
        "password": "TestPassword123"
    }

    client.post("/auth/register", json=register_payload)

    login_payload = {
        "username": register_payload["email"],
        "password": register_payload["password"]
    }

    login_response = client.post("/auth/login", data=login_payload)

    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert data["email"] == register_payload["email"]