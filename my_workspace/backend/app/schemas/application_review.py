from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class ReviewRequest(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected|under_review|pending_documents)$")
    remarks: Optional[str] = None

class ApplicationStaffListItem(BaseModel):
    id: UUID
    application_no: str
    applicant_name: str
    form_type: str
    status: str
    submitted_at: datetime
    requested_amount: Optional[float] = None

class PartyDetailSchema(BaseModel):
    role: str
    full_name: str
    position: Optional[str] = None
    department: Optional[str] = None
    has_signature: bool

class AttachmentSchema(BaseModel):
    id: UUID
    file_type: str
    original_filename: str
    mime_type: Optional[str] = None
    uploaded_at: datetime

class ApplicationStaffDetail(BaseModel):
    id: UUID
    application_no: str
    applicant_id: UUID
    form_type: str
    status: str
    form_data: dict
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    review_remarks: Optional[str] = None
    parties: List[PartyDetailSchema]
    attachments: List[AttachmentSchema] = []
