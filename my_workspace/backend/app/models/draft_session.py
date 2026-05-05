import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

DRAFT_EXPIRE_DAYS = 30


class DraftSession(Base):
    __tablename__ = "draft_sessions"
    __table_args__ = (
        UniqueConstraint("user_id", "form_type", name="uq_draft_user_form_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    form_type: Mapped[str] = mapped_column(String(20), nullable=False)

    form_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    current_step: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    last_saved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["User"] = relationship(back_populates="draft_sessions")

    @staticmethod
    def default_expires_at() -> datetime:
        return datetime.now(timezone.utc) + timedelta(days=DRAFT_EXPIRE_DAYS)
