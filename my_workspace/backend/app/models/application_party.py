import uuid
from sqlalchemy import ForeignKey, Integer, JSON, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ApplicationParty(Base):
    __tablename__ = "application_parties"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("loan_applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Optional — non-member parties (e.g. external guarantors) have no user record
    member_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=True,
    )

    role: Mapped[str] = mapped_column(String(50), nullable=False)   # BORROWER | GUARANTOR | SPOUSE_BORROWER
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[str | None] = mapped_column(String(100))
    department: Mapped[str | None] = mapped_column(String(100))
    national_id: Mapped[str | None] = mapped_column(String(20))
    address_snapshot: Mapped[dict | None] = mapped_column(JSON)
    sequence: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    application: Mapped["LoanApplication"] = relationship(back_populates="parties")
    signature: Mapped["Signature"] = relationship(
        back_populates="party",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ApplicationParty(role={self.role}, name={self.full_name})>"
