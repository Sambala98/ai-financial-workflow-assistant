from datetime import datetime
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    user_id: int
    original_filename: str
    stored_filename: str
    file_path: str
    content_type: str | None
    file_size: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentTextResponse(BaseModel):
    document_id: int
    original_filename: str
    extracted_text: str
    character_count: int

class DocumentChunkResponse(BaseModel):
    id: int
    document_id: int
    user_id: int
    chunk_index: int
    chunk_text: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentChunkCreateResponse(BaseModel):
    document_id: int
    total_chunks: int
    message: str