import uuid
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import LoanApplication, AuditLog, User
from app.models.attachment import Attachment
from app.services.pdf_service import PdfService
from loguru import logger

class EmergencyLoanService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pdf_service = PdfService()

    async def create_emergency_application(
        self,
        user_id: uuid.UUID,
        data: Dict[str, Any],
        draft_id: Optional[uuid.UUID] = None,
    ) -> LoanApplication:
        """
        Logic สำหรับการสร้างใบสมัครกู้ฉุกเฉิน (ลดรูปจากกู้สามัญ)
        """
        # 1. Validation เบื้องต้น (เช่น วงเงินไม่เกิน 50,000)
        loan_amount = data.get("step2", {}).get("loan_amount", 0)
        if loan_amount > 50000:
            raise ValueError("วงเงินกู้ฉุกเฉินต้องไม่เกิน 50,000 บาท")

        # 2. สร้าง Application No (EMG-YYYYMM-XXXX)
        from datetime import datetime
        now = datetime.now()
        prefix = f"EMG-{now.strftime('%Y%m')}"

        # ค้นหาลำดับถัดไป (Simplified logic)
        from sqlalchemy import func, select, update as sql_update
        count_stmt = select(func.count()).select_from(LoanApplication).where(LoanApplication.application_no.like(f"{prefix}%"))
        res = await self.db.execute(count_stmt)
        count = res.scalar()
        app_no = f"{prefix}-{str(count + 1).zfill(4)}"

        # 3. สร้าง Record
        app = LoanApplication(
            application_no=app_no,
            applicant_id=user_id,
            form_type="emergency",
            form_data=data,
            status="submitted",
            requested_amount=loan_amount,
            submitted_at=datetime.now()
        )
        self.db.add(app)
        await self.db.flush()  # Get ID before migrating attachments

        # 4. Migrate attachments: draft_session_id → loan_application_id
        if draft_id:
            stmt = (
                sql_update(Attachment)
                .where(Attachment.application_id == draft_id)
                .values(application_id=app.id)
            )
            result = await self.db.execute(stmt)
            logger.info(f"Migrated {result.rowcount} attachments: {draft_id} → {app.id}")

        await self.db.commit()
        await self.db.refresh(app)

        logger.info(f"Emergency Application {app_no} created for user {user_id}")
        return app
