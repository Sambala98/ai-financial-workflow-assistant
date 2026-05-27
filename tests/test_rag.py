import uuid
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_test_token():
    email = f"rag_test_user_{uuid.uuid4().hex}@example.com"
    password = "TestPassword123"

    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def test_rag_search_requires_auth():
    response = client.post(
        "/rag/search",
        json={
            "query": "What tools are used for background processing?",
            "top_k": 3,
        },
    )

    assert response.status_code == 401


def test_rag_answer_requires_auth():
    response = client.post(
        "/rag/answer",
        json={
            "question": "What tools are used for background processing?",
            "top_k": 3,
        },
    )

    assert response.status_code == 401


def test_rag_search_with_auth():
    token = create_test_token()

    response = client.post(
        "/rag/search",
        json={
            "query": "What tools are used for background processing?",
            "top_k": 3,
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == "What tools are used for background processing?"
    assert "results" in data
    assert isinstance(data["results"], list)


def test_rag_answer_with_auth():
    token = create_test_token()

    response = client.post(
        "/rag/answer",
        json={
            "question": "What tools are used for background processing?",
            "top_k": 3,
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == "What tools are used for background processing?"
    assert "answer" in data
    assert "sources" in data
    assert isinstance(data["sources"], list)