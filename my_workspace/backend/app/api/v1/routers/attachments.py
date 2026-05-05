from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, DbSession
from app.models import LoanApplication
from app.models.draft_session import DraftSession
from app.models.attachment import Attachment
from app.services.attachment_service import AttachmentService
from app.schemas.attachment import AttachmentResponse, AttachmentUploadResponse

router = APIRouter(prefix="/attachments", tags=["attachments"])


async def _verify_ownership(
    app_id: UUID, user_id: UUID, role: str, db: AsyncSession
) -> None:
    """
    ตรวจสอบว่า user เป็นเจ้าของ LoanApplication หรือ DraftSession ที่ระบุ
    รองรับทั้ง application_id และ draft_session_id เพราะ StepAttachments
    ส่ง draftId ขณะกรอกฟอร์ม (ก่อน submit) และ application_id หลัง submit
    """
    # ลองหา LoanApplication ก่อน
    result = await db.execute(select(LoanApplication).where(LoanApplication.id == app_id))
    loan_app = result.scalar_one_or_none()
    if loan_app:
        if loan_app.applicant_id != user_id and role != "staff":
            raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์ดำเนินการกับคำขอนี้")
        return

    # ลองหา DraftSession
    result = await db.execute(select(DraftSession).where(DraftSession.id == app_id))
    draft = result.scalar_one_or_none()
    if not draft:
        raise HTTPException(status_code=404, detail="ไม่พบคำขอหรือร่างที่ระบุ")
    if draft.user_id != user_id and role != "staff":
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์ดำเนินการกับคำขอนี้")


@router.post("/applications/{app_id}", response_model=AttachmentUploadResponse)
async def upload_attachment(
    app_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
    file_type: str = Form(...),
    file: UploadFile = File(...),
):
    await _verify_ownership(app_id, UUID(current_user["id"]), current_user["role"], db)

    service = AttachmentService(db)
    attachment = await service.upload_attachment(app_id, file_type, file)

    return {
        "success": True,
        "attachment_id": attachment.id,
        "message": "อัปโหลดเอกสารสำเร็จ"
    }


@router.get("/applications/{app_id}", response_model=List[AttachmentResponse])
async def list_attachments(
    app_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    await _verify_ownership(app_id, UUID(current_user["id"]), current_user["role"], db)

    service = AttachmentService(db)
    attachments = await service.get_application_attachments(app_id)

    return [
        AttachmentResponse(
            **a.__dict__,
            download_url=f"/api/v1/attachments/{a.id}/download"
        ) for a in attachments
    ]


@router.get("/{att_id}/download")
async def download_attachment(
    att_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    service = AttachmentService(db)
    att = await service.get_attachment(att_id)

    if not att:
        raise HTTPException(status_code=404, detail="ไม่พบไฟล์ที่ต้องการ")

    await _verify_ownership(
        att.application_id, UUID(current_user["id"]), current_user["role"], db
    )

    return FileResponse(
        path=att.storage_path,
        filename=att.original_filename,
        media_type=att.mime_type
    )


@router.delete("/{att_id}")
async def delete_attachment(
    att_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    service = AttachmentService(db)
    att = await service.get_attachment(att_id)

    if not att:
        raise HTTPException(status_code=404, detail="ไม่พบไฟล์ที่ต้องการลบ")

    # ตรวจสอบว่าเป็นเจ้าของ และ staff ไม่สามารถลบไฟล์ของ borrower ได้
    result = await db.execute(select(LoanApplication).where(LoanApplication.id == att.application_id))
    loan_app = result.scalar_one_or_none()
    if loan_app:
        if loan_app.applicant_id != UUID(current_user["id"]):
            raise HTTPException(status_code=403, detail="คุณไม่ใช่เจ้าของคำขอนี้")
    else:
        result = await db.execute(select(DraftSession).where(DraftSession.id == att.application_id))
        draft = result.scalar_one_or_none()
        if not draft or draft.user_id != UUID(current_user["id"]):
            raise HTTPException(status_code=403, detail="คุณไม่ใช่เจ้าของคำขอนี้")

    await service.delete_attachment(att_id)
    return {"success": True, "message": "ลบไฟล์สำเร็จ"}
