from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class AttachmentResponse(BaseModel):
    id: UUID
    file_type: str
    original_filename: str
    file_size_bytes: int
    mime_type: str
    uploaded_at: datetime
    download_url: str

class AttachmentUploadResponse(BaseModel):
    success: bool
    attachment_id: UUID
    message: str
