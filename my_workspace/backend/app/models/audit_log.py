import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"))

    # CREATE | UPDATE | SUBMIT | APPROVE | REJECT | CANCEL | LOGIN | LOGOUT
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(50))    # loan_application | member_profile
    entity_id: Mapped[uuid.UUID | None] = mapped_column(Uuid)

    old_values: Mapped[dict | None] = mapped_column(JSON)
    new_values: Mapped[dict | None] = mapped_column(JSON)
    ip_address: Mapped[str | None] = mapped_column(String(45))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    user: Mapped["User | None"] = relationship(back_populates="audit_logs")
