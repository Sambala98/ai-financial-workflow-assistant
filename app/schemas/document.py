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