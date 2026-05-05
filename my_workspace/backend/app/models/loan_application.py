import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Numeric, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    application_no: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    applicant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False, index=True)

    form_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)    # ordinary | emergency
    form_version: Mapped[str] = mapped_column(String(10), nullable=False, default="1.0")

    # สถานะ: draft → submitted → under_review → approved | rejected | cancelled
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", index=True)

    requested_amount: Mapped[float | None] = mapped_column(Numeric(12, 2))
    requested_installments: Mapped[int | None] = mapped_column(Integer)
    loan_purpose: Mapped[str | None] = mapped_column(Text)

    # ข้อมูลทั้งหมดของแบบฟอร์ม (all steps merged)
    form_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    # array of guarantor objects
    guarantors: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id"))
    review_remarks: Mapped[str | None] = mapped_column(Text)

    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancel_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # relationships
    applicant: Mapped["User"] = relationship(foreign_keys=[applicant_id], back_populates="applications")
    reviewer: Mapped["User | None"] = relationship(foreign_keys=[reviewed_by])
    parties: Mapped[list["ApplicationParty"]] = relationship(back_populates="application", cascade="all, delete-orphan")
    generated_pdf: Mapped["GeneratedPdf | None"] = relationship(back_populates="application", uselist=False, cascade="all, delete-orphan")
