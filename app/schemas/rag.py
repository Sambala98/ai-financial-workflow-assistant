from pydantic import BaseModel, Field


class RagSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)


class RagSourceChunk(BaseModel):
    chunk_id: int
    document_id: int
    chunk_index: int
    chunk_text: str
    distance: float | None = None


class RagSearchResponse(BaseModel):
    query: str
    results: list[RagSourceChunk]


class RagAnswerRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)


class RagAnswerResponse(BaseModel):
    question: str
    answer: str
    sources: list[RagSourceChunk]