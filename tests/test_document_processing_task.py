from unittest.mock import patch
import uuid
import pytest

from app.db.session import SessionLocal
from app.models.user import User
from app.models.document import Document, DocumentStatus
from app.models.document_chunk import DocumentChunk
from app.tasks.document_tasks import process_document_task


def test_process_document_task_saves_all_chunks():
    db = SessionLocal()

    try:
        user = User(
            email=f"task_test_user_{uuid.uuid4().hex}@example.com",
            hashed_password="fake-hashed-password",
            role="USER",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        document = Document(
            user_id=user.id,
            original_filename="multi-chunk-test.txt",
            stored_filename=f"{uuid.uuid4().hex}.txt",
            file_path="test-files/multi-chunk-test.txt",
            content_type="text/plain",
            file_size=300,
            status=DocumentStatus.UPLOADED,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        with patch(
            "app.tasks.document_tasks.extract_text_from_document",
            return_value="clean extracted text",
        ), patch(
            "app.tasks.document_tasks.chunk_text",
            return_value=["chunk one", "chunk two", "chunk three"],
        ), patch(
            "app.tasks.document_tasks.generate_embedding",
            return_value=[0.1] * 384,
        ):
            result = process_document_task.run(document.id)

        saved_chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document.id)
            .order_by(DocumentChunk.chunk_index)
            .all()
        )

        db.refresh(document)

        assert result["status"] == "success"
        assert result["chunks_created"] == 3
        assert document.status == DocumentStatus.PROCESSED
        assert len(saved_chunks) == 3

        assert saved_chunks[0].chunk_text == "chunk one"
        assert saved_chunks[1].chunk_text == "chunk two"
        assert saved_chunks[2].chunk_text == "chunk three"

    finally:
        db.close()

def test_process_document_task_marks_document_failed_when_embedding_fails():
    db = SessionLocal()

    try:
        user = User(
            email=f"task_failure_user_{uuid.uuid4().hex}@example.com",
            hashed_password="fake-hashed-password",
            role="USER",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        document = Document(
            user_id=user.id,
            original_filename="failure-test.txt",
            stored_filename=f"{uuid.uuid4().hex}.txt",
            file_path="test-files/failure-test.txt",
            content_type="text/plain",
            file_size=300,
            status=DocumentStatus.UPLOADED,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        with patch(
            "app.tasks.document_tasks.extract_text_from_document",
            return_value="clean extracted text",
        ), patch(
            "app.tasks.document_tasks.chunk_text",
            return_value=["chunk one"],
        ), patch(
            "app.tasks.document_tasks.generate_embedding",
            side_effect=Exception("Embedding failed"),
        ):
            with pytest.raises(Exception):
                process_document_task.run(document.id)

        db.refresh(document)

        saved_chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document.id)
            .all()
        )

        assert document.status == DocumentStatus.FAILED
        assert saved_chunks == []

    finally:
        db.close()