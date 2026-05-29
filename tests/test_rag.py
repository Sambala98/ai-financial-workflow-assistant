import uuid
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import SessionLocal
from app.models.document import Document, DocumentStatus
from app.models.document_chunk import DocumentChunk


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

def get_current_user_from_token(token: str):
    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    return response.json()


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

def test_rag_search_returns_inserted_relevant_chunk():
    token = create_test_token()
    current_user = get_current_user_from_token(token)
    user_id = current_user["id"]

    db = SessionLocal()

    try:
        document = Document(
            user_id=user_id,
            original_filename="background-processing.txt",
            stored_filename=f"{uuid.uuid4().hex}.txt",
            file_path="test-files/background-processing.txt",
            content_type="text/plain",
            file_size=120,
            status=DocumentStatus.PROCESSED,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        chunk = DocumentChunk(
            document_id=document.id,
            user_id=user_id,
            chunk_index=0,
            chunk_text="Redis and Celery are used for background document processing.",
            embedding=[0.1] * 384,
        )

        db.add(chunk)
        db.commit()

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
        assert len(data["results"]) >= 1
        assert "Redis and Celery" in data["results"][0]["chunk_text"]

    finally:
        db.close()
def test_rag_answer_returns_mocked_answer_with_sources():
    token = create_test_token()
    current_user = get_current_user_from_token(token)
    user_id = current_user["id"]

    db = SessionLocal()

    try:
        document = Document(
            user_id=user_id,
            original_filename="rag-answer-test.txt",
            stored_filename=f"{uuid.uuid4().hex}.txt",
            file_path="test-files/rag-answer-test.txt",
            content_type="text/plain",
            file_size=150,
            status=DocumentStatus.PROCESSED,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        chunk = DocumentChunk(
            document_id=document.id,
            user_id=user_id,
            chunk_index=0,
            chunk_text="Redis and Celery are used for background document processing.",
            embedding=[0.1] * 384,
        )

        db.add(chunk)
        db.commit()

        with patch(
            "app.api.rag.generate_llm_answer",
            return_value="Redis and Celery are used for background document processing.",
        ):
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
        assert data["answer"] == "Redis and Celery are used for background document processing."
        assert len(data["sources"]) >= 1

        assert any(
            "Redis and Celery" in source["chunk_text"]
            for source in data["sources"]
        )

    finally:
        db.close()
def test_rag_search_does_not_return_other_users_chunks():
    user_a_token = create_test_token()
    user_a = get_current_user_from_token(user_a_token)
    user_a_id = user_a["id"]

    user_b_token = create_test_token()

    db = SessionLocal()

    try:
        document = Document(
            user_id=user_a_id,
            original_filename="private-user-a-document.txt",
            stored_filename=f"{uuid.uuid4().hex}.txt",
            file_path="test-files/private-user-a-document.txt",
            content_type="text/plain",
            file_size=200,
            status=DocumentStatus.PROCESSED,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        chunk = DocumentChunk(
            document_id=document.id,
            user_id=user_a_id,
            chunk_index=0,
            chunk_text="Private User A financial document contains confidential invoice data.",
            embedding=[0.1] * 384,
        )

        db.add(chunk)
        db.commit()

        response = client.post(
            "/rag/search",
            json={
                "query": "What confidential invoice data is available?",
                "top_k": 5,
            },
            headers={
                "Authorization": f"Bearer {user_b_token}",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert all(
            "Private User A financial document" not in result["chunk_text"]
            for result in data["results"]
        )

    finally:
        db.close()