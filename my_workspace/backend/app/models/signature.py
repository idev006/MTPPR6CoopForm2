import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Signature(Base):
    __tablename__ = "signatures"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    party_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("application_parties.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    signature_data: Mapped[str] = mapped_column(Text, nullable=False)  # base64 PNG
    ip_address: Mapped[str | None] = mapped_column(String(50))
    user_agent: Mapped[str | None] = mapped_column(String(255))
    signed_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    # Relationship
    party: Mapped["ApplicationParty"] = relationship(back_populates="signature")

    def __repr__(self) -> str:
        return f"<Signature(party_id={self.party_id}, signed_at={self.signed_at})>"
