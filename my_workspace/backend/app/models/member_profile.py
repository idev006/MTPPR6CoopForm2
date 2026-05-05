import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MemberProfile(Base):
    __tablename__ = "member_profiles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Type A — กรอกเองได้
    title: Mapped[str | None] = mapped_column(String(50))   # ยศ/คำนำหน้า
    position: Mapped[str | None] = mapped_column(String(100))
    department: Mapped[str | None] = mapped_column(String(200))
    organization: Mapped[str | None] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(20))
    addr_house_no: Mapped[str | None] = mapped_column(String(20))
    addr_moo: Mapped[str | None] = mapped_column(String(10))
    addr_road: Mapped[str | None] = mapped_column(String(100))
    addr_tambon: Mapped[str | None] = mapped_column(String(100))
    addr_amphur: Mapped[str | None] = mapped_column(String(100))
    addr_province: Mapped[str | None] = mapped_column(String(100))

    # Type B — staff กรอกเท่านั้น
    salary: Mapped[float | None] = mapped_column(Numeric(12, 2))
    shares_amount: Mapped[float | None] = mapped_column(Numeric(12, 2))
    existing_debt: Mapped[float | None] = mapped_column(Numeric(12, 2))

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="profile")
