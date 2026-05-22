from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.document_text_service import extract_text_from_document
from app.services.chunking_service import chunk_text
from app.services.embedding_service import generate_embedding


@celery_app.task(bind=True, max_retries=3)
def process_document_task(self, document_id: int):
    db = SessionLocal()

    try:
        document = db.query(Document).filter(Document.id == document_id).first()

        if not document:
            return {"status": "failed", "reason": "Document not found"}

        document.status = "PROCESSING"
        db.commit()

        
        extracted_text = extract_text_from_document(
            document.file_path,
            document.content_type
)
        chunks = chunk_text(extracted_text)

        db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id,
            DocumentChunk.user_id == document.user_id,
        ).delete()

        for index, chunk in enumerate(chunks):
          embedding = generate_embedding(chunk)

          db_chunk = DocumentChunk(
            document_id=document_id,
            user_id=document.user_id,
            chunk_index=index,
            chunk_text=chunk,
            embedding=embedding,
    )
        db.add(db_chunk)

        document.status = "PROCESSED"
        db.commit()

        return {
            "status": "success",
            "document_id": document_id,
            "chunks_created": len(chunks),
        }

    except Exception as exc:
        db.rollback()

        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.status = "FAILED"
            db.commit()

        raise self.retry(exc=exc, countdown=10)

    finally:
        db.close()