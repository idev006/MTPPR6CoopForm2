import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # ประเภทการแจ้งเตือน: info | success | warning | error
    type: Mapped[str] = mapped_column(String(20), default="info")
    
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    link: Mapped[str | None] = mapped_column(String(500)) # ลิงก์ไปยังใบสมัครที่เกี่ยวข้อง
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # relationship
    user: Mapped["User"] = relationship(back_populates="notifications")
