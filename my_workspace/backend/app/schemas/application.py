from pydantic import BaseModel, field_validator
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime


class OrdinaryLoanSubmit(BaseModel):
    step1: Dict[str, Any]
    step2: Dict[str, Any]
    step3: Dict[str, Any]
    step4: Dict[str, Any]
    step5: Dict[str, Any]
    step6: Dict[str, Any]
    draft_id: Optional[UUID] = None  # ใช้ migrate attachments จาก draft → loan_application


class EmergencyLoanSubmit(BaseModel):
    step1: Dict[str, Any]
    step2: Dict[str, Any]
    step4: Dict[str, Any]
    draft_id: Optional[UUID] = None  # ใช้ migrate attachments จาก draft → loan_application


class ApplicationResponse(BaseModel):
    success: bool
    application_no: str
    application_id: str
    message: str


class ApplicationMeResponse(BaseModel):
    id: UUID
    application_no: str
    form_type: str
    status: str
    created_at: datetime


class CancelRequest(BaseModel):
    reason: Optional[str] = None

    @field_validator("reason")
    @classmethod
    def reason_max_length(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v.strip()) > 500:
            raise ValueError("เหตุผลต้องไม่เกิน 500 ตัวอักษร")
        return v.strip() if v else None


class ApplicationDetailResponse(BaseModel):
    id: UUID
    application_no: str
    form_type: str
    status: str
    requested_amount: Optional[float]
    requested_installments: Optional[int]
    loan_purpose: Optional[str]
    created_at: datetime
    submitted_at: Optional[datetime]
    reviewed_at: Optional[datetime]
    review_remarks: Optional[str]
    cancelled_at: Optional[datetime] = None
    cancel_reason: Optional[str] = None
    has_pdf: bool = False

    class Config:
        from_attributes = True
