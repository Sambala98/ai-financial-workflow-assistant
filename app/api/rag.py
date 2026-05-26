from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.document_chunk import DocumentChunk
from app.models.user import User
from app.api.dependencies import get_current_user
from app.schemas.rag import (
    RagSearchRequest,
    RagSearchResponse,
    RagSourceChunk,
    RagAnswerRequest,
    RagAnswerResponse,
)
from app.services.embedding_service import generate_embedding
from app.services.llm_service import generate_llm_answer

router = APIRouter(prefix="/rag", tags=["RAG"])


def search_relevant_chunks(
    db: Session,
    user_id: int,
    query: str,
    top_k: int,
) -> list[dict]:
    query_embedding = generate_embedding(query)

    results = (
        db.query(
            DocumentChunk.id.label("chunk_id"),
            DocumentChunk.document_id.label("document_id"),
            DocumentChunk.chunk_index.label("chunk_index"),
            DocumentChunk.chunk_text.label("chunk_text"),
            DocumentChunk.embedding.cosine_distance(query_embedding).label("distance"),
        )
        .filter(DocumentChunk.user_id == user_id)
        .filter(DocumentChunk.embedding.isnot(None))
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(top_k)
        .all()
    )

    chunks = []

    for row in results:
        chunks.append(
            {
                "chunk_id": row.chunk_id,
                "document_id": row.document_id,
                "chunk_index": row.chunk_index,
                "chunk_text": row.chunk_text,
                "distance": float(row.distance) if row.distance is not None else None,
            }
        )

    return chunks


@router.post("/search", response_model=RagSearchResponse)
def rag_search(
    request: RagSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chunks = search_relevant_chunks(
        db=db,
        user_id=current_user.id,
        query=request.query,
        top_k=request.top_k,
    )

    sources = [RagSourceChunk(**chunk) for chunk in chunks]

    return RagSearchResponse(
        query=request.query,
        results=sources,
    )


@router.post("/answer", response_model=RagAnswerResponse)
def rag_answer(
    request: RagAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chunks = search_relevant_chunks(
        db=db,
        user_id=current_user.id,
        query=request.question,
        top_k=request.top_k,
    )

    answer = generate_llm_answer(
        question=request.question,
        source_chunks=chunks,
    )

    sources = [RagSourceChunk(**chunk) for chunk in chunks]

    return RagAnswerResponse(
        question=request.question,
        answer=answer,
        sources=sources,
    )