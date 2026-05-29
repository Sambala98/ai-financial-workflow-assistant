import pytest

from app.db.session import SessionLocal
from app.models.document_chunk import DocumentChunk
from app.models.document import Document
from app.models.user import User


@pytest.fixture(autouse=True)
def clean_test_database():
    db = SessionLocal()

    try:
        db.query(DocumentChunk).delete()
        db.query(Document).delete()
        db.query(User).delete()

        db.commit()

        yield

        db.query(DocumentChunk).delete()
        db.query(Document).delete()
        db.query(User).delete()

        db.commit()

    finally:
        db.close()