from pathlib import Path
from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.concurrency import run_in_threadpool
from typing import List, Optional

from app.core.dependencies import CurrentUser, DbSession
from app.core.config import settings
from app.models import LoanApplication, User, AuditLog
from app.schemas.application import (
    OrdinaryLoanSubmit, EmergencyLoanSubmit,
    ApplicationResponse, ApplicationMeResponse, ApplicationDetailResponse,
    CancelRequest,
)
from app.services.application_service import ApplicationService
from app.services.emergency_loan_service import EmergencyLoanService
from app.services.notification_service import NotificationService
from app.services.pdf_service import PdfService
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("/ordinary/preview", status_code=200)
async def preview_ordinary_loan(
    data: OrdinaryLoanSubmit,
    current_user: CurrentUser,
):
    """สร้าง PDF ตัวอย่างสำหรับผู้กู้ตรวจสอบก่อน submit (ไม่บันทึก DB)."""
    user_id = current_user["id"]
    pdf_service = PdfService()
    try:
        await run_in_threadpool(
            pdf_service.generate_preview_pdf,
            data.model_dump(),
            user_id,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="ไม่พบไฟล์ template PDF กรุณาแจ้งผู้ดูแลระบบ")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ไม่สามารถสร้าง PDF ตัวอย่างได้: {str(e)}")
    return {"preview_ready": True, "message": "PDF ตัวอย่างพร้อมแล้ว"}


@router.get("/preview/exists")
async def preview_exists(current_user: CurrentUser):
    """ตรวจสอบว่ามีไฟล์ preview อยู่หรือไม่ (ไม่ดาวน์โหลดไฟล์)"""
    user_id = current_user["id"]
    preview_path = Path(settings.DATA_DIR) / "previews" / f"{user_id}.pdf"
    return {"exists": preview_path.exists()}


@router.get("/preview/download")
async def download_preview(current_user: CurrentUser):
    """ดาวน์โหลด PDF ตัวอย่างที่สร้างล่าสุดของผู้กู้"""
    user_id = current_user["id"]
    preview_path = Path(settings.DATA_DIR) / "previews" / f"{user_id}.pdf"
    if not preview_path.exists():
        raise HTTPException(status_code=404, detail="ไม่พบไฟล์ตัวอย่าง กรุณากดสร้างตัวอย่าง PDF ก่อน")
    return FileResponse(
        path=preview_path,
        media_type="application/pdf",
        filename="ตัวอย่าง-แบบขอกู้สามัญ.pdf",
    )


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def submit_application(
    data: OrdinaryLoanSubmit,
    current_user: CurrentUser,
    db: DbSession,
):
    service = ApplicationService(db)
    try:
        app = await service.submit_ordinary_loan(UUID(current_user["id"]), data)  # draft_id included in data
        return {
            "success": True,
            "application_no": app.application_no,
            "application_id": str(app.id),
            "message": "ยื่นคำขอกู้เงินสำเร็จเรียบร้อยแล้ว"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาดในการส่งคำขอ: {str(e)}"
        )


@router.post("/emergency", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def submit_emergency_application(
    data: EmergencyLoanSubmit,
    current_user: CurrentUser,
    db: DbSession,
):
    service = EmergencyLoanService(db)
    try:
        app = await service.create_emergency_application(
            UUID(current_user["id"]),
            data.model_dump(),
            draft_id=data.draft_id,
        )
        return {
            "success": True,
            "application_no": app.application_no,
            "application_id": str(app.id),
            "message": "ยื่นคำขอกู้ฉุกเฉินสำเร็จเรียบร้อยแล้ว"
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาดในการส่งคำขอ: {str(e)}"
        )


@router.get("/me", response_model=List[ApplicationMeResponse])
async def get_my_applications(
    current_user: CurrentUser,
    db: DbSession,
):
    result = await db.execute(
        select(LoanApplication)
        .where(LoanApplication.applicant_id == UUID(current_user["id"]))
        .order_by(LoanApplication.created_at.desc())
    )
    apps = result.scalars().all()
    return apps


@router.get("/{app_id}", response_model=ApplicationDetailResponse)
async def get_application_detail(
    app_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    result = await db.execute(
        select(LoanApplication)
        .options(selectinload(LoanApplication.generated_pdf))
        .where(LoanApplication.id == app_id)
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="ไม่พบคำขอ")
    if app.applicant_id != UUID(current_user["id"]):
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์เข้าถึงคำขอนี้")

    return ApplicationDetailResponse(
        id=app.id,
        application_no=app.application_no,
        form_type=app.form_type,
        status=app.status,
        requested_amount=float(app.requested_amount) if app.requested_amount is not None else None,
        requested_installments=app.requested_installments,
        loan_purpose=app.loan_purpose,
        created_at=app.created_at,
        submitted_at=app.submitted_at,
        reviewed_at=app.reviewed_at,
        review_remarks=app.review_remarks,
        has_pdf=app.generated_pdf is not None,
    )


@router.post("/{app_id}/resubmit", status_code=200)
async def resubmit_application(
    app_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Borrower ส่งเอกสารเพิ่มเติมหลังจาก staff ทำ pending_documents
    — รีเซ็ต status กลับเป็น submitted และแจ้งเตือน staff ทุกคน
    """
    result = await db.execute(select(LoanApplication).where(LoanApplication.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="ไม่พบคำขอ")
    if app.applicant_id != UUID(current_user["id"]):
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์ดำเนินการกับคำขอนี้")
    if app.status != "pending_documents":
        raise HTTPException(
            status_code=400,
            detail=f"ไม่สามารถส่งเอกสารเพิ่มได้ในสถานะ '{app.status}'"
        )

    # Reset status
    app.status = "submitted"
    app.updated_at = datetime.now(timezone.utc)

    # Audit log
    db.add(AuditLog(
        user_id=UUID(current_user["id"]),
        action="RESUBMIT",
        entity_type="loan_application",
        entity_id=app_id,
        old_values={"status": "pending_documents"},
        new_values={"status": "submitted"},
    ))

    await db.commit()

    # Notify all staff
    try:
        staff_result = await db.execute(select(User).where(User.role == "staff", User.is_active == True))
        staff_users = staff_result.scalars().all()
        borrower_result = await db.execute(select(User).where(User.id == app.applicant_id))
        borrower = borrower_result.scalar_one_or_none()
        borrower_name = f"{borrower.first_name} {borrower.last_name}" if borrower else "ผู้กู้"

        notif_svc = NotificationService(db)
        for staff in staff_users:
            await notif_svc.create_notification(
                user_id=staff.id,
                title=f"ส่งเอกสารเพิ่มแล้ว — {app.application_no}",
                message=f"ผู้กู้ {borrower_name} ได้ส่งเอกสารเพิ่มเติมสำหรับคำขอ {app.application_no} แล้ว กรุณาตรวจสอบ",
                type="info",
                link=f"/staff/applications/{app_id}",
            )
    except Exception:
        pass  # notification failure must not block

    return {"success": True, "message": "ส่งเอกสารเพิ่มเติมเรียบร้อยแล้ว รอเจ้าหน้าที่ตรวจสอบ"}


@router.post("/{app_id}/cancel", status_code=200)
async def cancel_application(
    app_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
    body: Optional[CancelRequest] = Body(default=None),
):
    result = await db.execute(select(LoanApplication).where(LoanApplication.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="ไม่พบคำขอ")
    if app.applicant_id != UUID(current_user["id"]):
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์ดำเนินการกับคำขอนี้")
    if app.status != "submitted":
        raise HTTPException(
            status_code=400,
            detail=f"ไม่สามารถยกเลิกคำขอที่มีสถานะ '{app.status}' ได้"
        )

    reason = body.reason if body else None
    now = datetime.now(timezone.utc)
    app.status = "cancelled"
    app.cancelled_at = now
    app.cancel_reason = reason
    app.updated_at = now

    # Audit log
    db.add(AuditLog(
        user_id=UUID(current_user["id"]),
        action="CANCEL",
        entity_type="loan_application",
        entity_id=app_id,
        old_values={"status": "submitted"},
        new_values={"status": "cancelled", "reason": reason},
    ))

    await db.commit()

    # แจ้ง Staff ทุกคนว่าผู้กู้ยกเลิก
    try:
        staff_result = await db.execute(select(User).where(User.role == "staff", User.is_active == True))
        staff_users = staff_result.scalars().all()
        borrower_result = await db.execute(select(User).where(User.id == app.applicant_id))
        borrower = borrower_result.scalar_one_or_none()
        borrower_name = f"{borrower.first_name} {borrower.last_name}" if borrower else "ผู้กู้"

        notif_svc = NotificationService(db)
        reason_suffix = f" — เหตุผล: {body.reason}" if body.reason else ""
        for staff in staff_users:
            await notif_svc.create_notification(
                user_id=staff.id,
                title=f"ยกเลิกคำขอ — {app.application_no}",
                message=f"ผู้กู้ {borrower_name} ได้ยกเลิกคำขอ {app.application_no}{reason_suffix}",
                type="warning",
                link=f"/staff/applications/{app_id}",
            )
    except Exception:
        pass  # notification failure must not block

    return {"success": True, "message": "ยกเลิกคำขอเรียบร้อยแล้ว"}
