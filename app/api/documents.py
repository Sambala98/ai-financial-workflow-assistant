import os
import shutil
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentResponse, DocumentTextResponse
from app.services.document_text_service import extract_text_from_document
from app.models.document_chunk import DocumentChunk
from app.models.document import DocumentStatus
from app.schemas.document import (
    DocumentResponse,
    DocumentTextResponse,
    DocumentChunkResponse,
    DocumentChunkCreateResponse,
)
from app.services.document_text_service import (
    extract_text_from_document,
    split_text_into_chunks,
)
from app.tasks.document_tasks import process_document_task


router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = "uploaded_files"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED
)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    allowed_types = [
        "application/pdf",
        "text/plain",
        "text/csv"
    ]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, TXT, and CSV files are allowed"
        )

    file_extension = os.path.splitext(file.filename)[1]
    stored_filename = f"{uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, stored_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)

    document = Document(
        user_id=current_user.id,
        original_filename=file.filename,
        stored_filename=stored_filename,
        file_path=file_path,
        content_type=file.content_type,
        file_size=file_size
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


@router.get(
    "",
    response_model=list[DocumentResponse],
    status_code=status.HTTP_200_OK
)
def get_my_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Document).filter(Document.user_id == current_user.id).all()


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    return document

@router.post(
    "/{document_id}/extract-text",
    response_model=DocumentTextResponse,
    status_code=status.HTTP_200_OK
)
def extract_document_text(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    try:
        extracted_text = extract_text_from_document(
            file_path=document.file_path,
            content_type=document.content_type
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Uploaded file not found on server"
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type"
        )

    return {
        "document_id": document.id,
        "original_filename": document.original_filename,
        "extracted_text": extracted_text[:5000],
        "character_count": len(extracted_text)
    }

@router.post(
    "/{document_id}/chunks",
    response_model=DocumentChunkCreateResponse,
    status_code=status.HTTP_201_CREATED
)
def create_document_chunks(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    existing_chunks = db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document.id,
        DocumentChunk.user_id == current_user.id
    ).all()

    if existing_chunks:
        for chunk in existing_chunks:
            db.delete(chunk)

        db.commit()

    try:
        extracted_text = extract_text_from_document(
            file_path=document.file_path,
            content_type=document.content_type
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Uploaded file not found on server"
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type"
        )

    chunks = split_text_into_chunks(extracted_text)

    for index, chunk_text in enumerate(chunks):
        chunk = DocumentChunk(
            document_id=document.id,
            user_id=current_user.id,
            chunk_index=index,
            chunk_text=chunk_text
        )
        db.add(chunk)

    document.status = DocumentStatus.PROCESSED

    db.commit()

    return {
        "document_id": document.id,
        "total_chunks": len(chunks),
        "message": "Document chunks created successfully"
    }


@router.get(
    "/{document_id}/chunks",
    response_model=list[DocumentChunkResponse],
    status_code=status.HTTP_200_OK
)
def get_document_chunks(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    return db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document.id,
        DocumentChunk.user_id == current_user.id
    ).order_by(DocumentChunk.chunk_index).all()

@router.post("/{document_id}/process")
def process_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id,
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    task = process_document_task.delay(document_id)

    return {
        "message": "Document processing started",
        "document_id": document_id,
        "task_id": task.id,
        "status": "PROCESSING",
    }

@router.get("/{document_id}/status")
def get_document_status(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id,
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "document_id": document.id,
        "original_filename": document.original_filename,
        "status": document.status,
    }