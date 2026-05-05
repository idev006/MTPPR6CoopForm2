import datetime
import uuid
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update as sql_update
from loguru import logger
from fastapi.concurrency import run_in_threadpool

from app.models import LoanApplication, ApplicationParty, Signature, User, MemberProfile
from app.models.attachment import Attachment
from app.schemas.application import OrdinaryLoanSubmit
from app.services.pdf_service import PdfService
from app.services.notification_service import NotificationService

class ApplicationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pdf_service = PdfService()

    async def submit_ordinary_loan(self, user_id: uuid.UUID, data: OrdinaryLoanSubmit) -> LoanApplication:
        """
        Orchestrate the submission of an Ordinary Loan Application (Async version).
        """
        try:
            # 1. Generate Application No
            app_no = self._generate_app_no("ORD")

            # 2. Create Application Header
            db_app = LoanApplication(
                application_no=app_no,
                applicant_id=user_id,
                form_type="ordinary",
                status="submitted",
                requested_amount=float(data.step2.get("loan_amount", 0)),
                requested_installments=int(data.step2.get("repayment_period", 0)),
                form_data=data.model_dump(),
                submitted_at=datetime.datetime.now(datetime.timezone.utc)
            )
            self.db.add(db_app)
            await self.db.flush() # Get ID

            # 3. Snapshot Parties & Signatures
            await self._create_parties_and_signatures(db_app, data, user_id)

            # 4. Migrate attachments: draft_session_id → loan_application_id
            #    Borrower upload ระหว่างกรอก wizard โดยใช้ draft_id เป็น application_id
            #    ต้องย้ายมาใช้ loan_app.id เพื่อให้ staff เห็นเอกสาร
            if data.draft_id:
                await self._migrate_attachments(data.draft_id, db_app.id)

            # 5. Generate PDF in threadpool to avoid blocking
            try:
                await run_in_threadpool(
                    self.pdf_service.generate_ordinary_loan_pdf,
                    data.model_dump(),
                    app_no
                )
            except Exception as pdf_err:
                logger.error(f"PDF Generation failed: {pdf_err}")

            await self.db.commit()
            await self.db.refresh(db_app)

            # Notify all staff users about the new application
            await self._notify_staff_new_application(db_app, data)

            return db_app

        except Exception as e:
            await self.db.rollback()
            logger.exception(f"Submission failed: {e}")
            raise

    async def _migrate_attachments(self, from_id: uuid.UUID, to_id: uuid.UUID) -> None:
        """
        ย้าย Attachment.application_id จาก draft_session_id → loan_application_id
        เรียกตอน submit เพื่อให้ staff มองเห็นเอกสารแนบของผู้กู้
        """
        stmt = (
            sql_update(Attachment)
            .where(Attachment.application_id == from_id)
            .values(application_id=to_id)
        )
        result = await self.db.execute(stmt)
        logger.info(f"Migrated {result.rowcount} attachments: {from_id} → {to_id}")

    async def _notify_staff_new_application(self, app: LoanApplication, data: OrdinaryLoanSubmit):
        """Send notification to all active staff users when a new loan application is submitted."""
        try:
            stmt = select(User).where(User.role == "staff", User.is_active == True)
            result = await self.db.execute(stmt)
            staff_users = result.scalars().all()

            if not staff_users:
                return

            s1 = data.step1
            borrower_name = f"{s1.get('title', '')}{s1.get('first_name', '')} {s1.get('last_name', '')}".strip()
            amount = float(data.step2.get("loan_amount", 0))
            amount_str = f"{amount:,.0f}" if amount else "—"

            notif_svc = NotificationService(self.db)
            for staff in staff_users:
                await notif_svc.create_notification(
                    user_id=staff.id,
                    title=f"คำขอกู้สามัญใหม่ — {app.application_no}",
                    message=f"ผู้กู้: {borrower_name} ยอดขอกู้: {amount_str} บาท กรุณาตรวจสอบในระบบ",
                    type="info",
                    link=f"/staff/applications/{app.id}",
                )
            logger.info(f"Notified {len(staff_users)} staff users about new application {app.application_no}")
        except Exception as e:
            # Notification failure must not fail the submission itself
            logger.warning(f"Staff notification failed for app {app.id}: {e}")

    async def _create_parties_and_signatures(self, app: LoanApplication, data: OrdinaryLoanSubmit, user_id: uuid.UUID):
        """
        Create structured snapshots for all parties.
        """
        s1 = data.step1
        s3 = data.step3
        s4 = data.step4

        # Party 1: Borrower Snapshot
        result = await self.db.execute(select(MemberProfile).where(MemberProfile.user_id == user_id))
        profile = result.scalar_one_or_none()
        
        borrower = ApplicationParty(
            application_id=app.id,
            member_id=app.applicant_id,
            role="BORROWER",
            full_name=f"{s1.get('title')} {s1.get('first_name')} {s1.get('last_name')}",
            position=s1.get("position") or (profile.position if profile else None),
            department=s1.get("department") or (profile.department if profile else None),
            national_id=s1.get("id_card"),
            address_snapshot={"current": s1.get("current_addr"), "register": s1.get("register_addr")}
        )
        self.db.add(borrower)
        await self.db.flush()

        if s4.get("borrower_sig", {}).get("signed"):
            self.db.add(Signature(party_id=borrower.id, signature_data=s4["borrower_sig"]["signature_base64"]))

        # Party 2: Borrower Spouse
        if s1.get("marital_status") == "married":
            spouse = ApplicationParty(
                application_id=app.id,
                role="SPOUSE_BORROWER",
                full_name=s1.get("spouse_name", "คู่สมรส")
            )
            self.db.add(spouse)
            await self.db.flush()
            if s4.get("spouse_sig", {}).get("signed"):
                self.db.add(Signature(party_id=spouse.id, signature_data=s4["spouse_sig"]["signature_base64"]))

        # Party 3-N: Guarantors
        for i, g in enumerate(s3.get("guarantors", [])):
            party_g = ApplicationParty(
                application_id=app.id,
                role="GUARANTOR",
                full_name=g.get("name"),
                position=g.get("position"),
                department=g.get("department"),
                national_id=g.get("id_card"),
                address_snapshot=g.get("current_addr"),
                sequence=i+1
            )
            self.db.add(party_g)
            await self.db.flush()

    def _generate_app_no(self, prefix: str) -> str:
        year = (datetime.datetime.now().year + 543) % 100
        uid = str(uuid.uuid4())[:4].upper()
        return f"{prefix}-{year}-{uid}"
