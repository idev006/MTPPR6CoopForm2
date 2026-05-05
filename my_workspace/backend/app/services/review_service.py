from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from loguru import logger

from app.models import LoanApplication, AuditLog, User, ApplicationParty
from app.models.attachment import Attachment
from app.schemas.application_review import ReviewRequest
from app.services.pdf_service import PdfService
from fastapi.concurrency import run_in_threadpool

class ReviewService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pdf_service = PdfService()

    # ... (existing methods) ...

    async def regenerate_pdf(self, app_id: UUID):
        stmt = select(LoanApplication).where(LoanApplication.id == app_id)
        result = await self.db.execute(stmt)
        app = result.scalar_one_or_none()
        if not app: raise ValueError("Application not found")

        # Re-run engine in threadpool
        await run_in_threadpool(
            self.pdf_service.generate_ordinary_loan_pdf, 
            app.form_data, 
            app.application_no
        )
        logger.info(f"PDF Re-generated for app {app_id}")

    async def get_applications_for_staff(self, status: str | None = None) -> list:
        stmt = (
            select(LoanApplication, User.first_name, User.last_name)
            .join(User, LoanApplication.applicant_id == User.id)
            .order_by(LoanApplication.submitted_at.desc())
        )
        if status:
            stmt = stmt.where(LoanApplication.status == status)
        result = await self.db.execute(stmt)

        items = []
        for app, first_name, last_name in result:
            items.append({
                "id": app.id,
                "application_no": app.application_no,
                "applicant_name": f"{first_name} {last_name}",
                "form_type": app.form_type,
                "status": app.status,
                "submitted_at": app.submitted_at,
                "requested_amount": float(app.requested_amount) if app.requested_amount else None,
            })
        return items

    async def get_application_detail(self, app_id: UUID) -> dict:
        stmt = select(LoanApplication).where(LoanApplication.id == app_id)
        result = await self.db.execute(stmt)
        app = result.scalar_one_or_none()
        if not app:
            return None

        stmt_p = select(ApplicationParty).where(ApplicationParty.application_id == app_id)
        result_p = await self.db.execute(stmt_p)
        parties = result_p.scalars().all()

        stmt_a = select(Attachment).where(Attachment.application_id == app_id).order_by(Attachment.uploaded_at)
        result_a = await self.db.execute(stmt_a)
        attachments = result_a.scalars().all()

        return {
            "id": app.id,
            "application_no": app.application_no,
            "applicant_id": app.applicant_id,
            "form_type": app.form_type,
            "status": app.status,
            "form_data": app.form_data,
            "submitted_at": app.submitted_at,
            "reviewed_at": app.reviewed_at,
            "review_remarks": app.review_remarks,
            "parties": [
                {
                    "role": p.role,
                    "full_name": p.full_name,
                    "position": p.position,
                    "department": p.department,
                    "has_signature": True,
                } for p in parties
            ],
            "attachments": [
                {
                    "id": a.id,
                    "file_type": a.file_type,
                    "original_filename": a.original_filename,
                    "mime_type": a.mime_type,
                    "uploaded_at": a.uploaded_at,
                } for a in attachments
            ],
        }

    async def update_status(self, app_id: UUID, staff_user: dict, req: ReviewRequest, ip: str = None):
        """
        Update application status and record audit log.
        """
        staff_id = UUID(staff_user["id"])

        stmt = select(LoanApplication).where(LoanApplication.id == app_id)
        result = await self.db.execute(stmt)
        app = result.scalar_one_or_none()
        if not app:
            raise ValueError("Application not found")

        old_status = app.status
        new_status = req.status

        # 1. Update Application
        app.status = new_status
        app.reviewed_by = staff_id
        app.reviewed_at = datetime.now(timezone.utc)
        app.review_remarks = req.remarks

        # 2. Create Audit Log
        log = AuditLog(
            user_id=staff_id,
            action=new_status.upper(),
            entity_type="loan_application",
            entity_id=app_id,
            old_values={"status": old_status},
            new_values={"status": new_status, "remarks": req.remarks},
            ip_address=ip
        )
        self.db.add(log)

        # 3. Send Notification to Borrower
        from app.services.notification_service import NotificationService
        notif_service = NotificationService(self.db)
        
        STATUS_CONFIG = {
            "approved":           ("อนุมัติแล้ว",           "success", "คำขอกู้เงินเลขที่ {no} ได้รับการอนุมัติแล้ว"),
            "rejected":           ("ไม่อนุมัติ",             "error",   "คำขอกู้เงินเลขที่ {no} ถูกปฏิเสธ"),
            "under_review":       ("กำลังพิจารณา",          "info",    "คำขอกู้เงินเลขที่ {no} อยู่ระหว่างการพิจารณาของเจ้าหน้าที่"),
            "pending_documents":  ("รอเอกสารเพิ่มเติม",    "warning", "เจ้าหน้าที่ขอเอกสารเพิ่มเติมสำหรับคำขอเลขที่ {no} กรุณาตรวจสอบรายละเอียด"),
        }
        label, notif_type, msg_tpl = STATUS_CONFIG.get(new_status, (new_status, "info", "สถานะคำขอ {no} เปลี่ยนเป็น " + new_status))
        message = msg_tpl.format(no=app.application_no)
        if req.remarks:
            message += f" — หมายเหตุ: {req.remarks}"

        await notif_service.create_notification(
            user_id=app.applicant_id,
            title=f"ใบสมัคร {app.application_no} — {label}",
            message=message,
            type=notif_type,
            link=f"/applications/{app_id}",
        )
        
        await self.db.commit()
        staff_id = staff_user["id"] if isinstance(staff_user, dict) else str(staff_user.id)
        logger.info(f"Staff {staff_id} updated App {app_id} to {new_status}")
        return app
