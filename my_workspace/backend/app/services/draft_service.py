from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.attachment import Attachment
from app.models.draft_session import DraftSession
from loguru import logger


# ─── Attachment cascade helper ────────────────────────────────────────────────

async def _delete_attachments_for(draft_id: UUID, db: AsyncSession) -> int:
    """
    ลบไฟล์บน disk + record ใน DB ของ Attachment ทั้งหมดที่เป็นของ draft นี้
    คืน rowcount ที่ถูกลบ
    """
    result = await db.execute(
        select(Attachment).where(Attachment.application_id == draft_id)
    )
    attachments = result.scalars().all()

    deleted = 0
    for att in attachments:
        p = Path(att.storage_path)
        if p.exists():
            try:
                p.unlink()
            except OSError as e:
                logger.warning(f"Cannot delete file {p}: {e}")
        await db.delete(att)
        deleted += 1

    if deleted:
        logger.info(f"Deleted {deleted} attachment(s) for draft {draft_id}")
    return deleted


# ─── Public functions ──────────────────────────────────────────────────────────

async def delete_expired_drafts(db: AsyncSession) -> int:
    """
    ลบ DraftSession ที่หมดอายุ พร้อม Attachment ที่เกี่ยวข้อง
    คืนจำนวน draft ที่ถูกลบ
    """
    result = await db.execute(
        select(DraftSession).where(DraftSession.expires_at < datetime.now(timezone.utc))
    )
    expired_drafts = result.scalars().all()

    if not expired_drafts:
        return 0

    total_att = 0
    for draft in expired_drafts:
        total_att += await _delete_attachments_for(draft.id, db)
        await db.delete(draft)

    await db.commit()
    logger.info(
        f"Cleanup expired drafts: {len(expired_drafts)} draft(s), {total_att} attachment(s) deleted"
    )
    return len(expired_drafts)


async def get_or_create_draft(user_id: UUID, form_type: str, db: AsyncSession) -> DraftSession:
    result = await db.execute(
        select(DraftSession).where(
            DraftSession.user_id == user_id,
            DraftSession.form_type == form_type,
        )
    )
    draft = result.scalar_one_or_none()
    if draft is None:
        draft = DraftSession(
            user_id=user_id,
            form_type=form_type,
            form_data={},
            current_step=1,
            expires_at=DraftSession.default_expires_at(),
        )
        db.add(draft)
        await db.commit()
        await db.refresh(draft)
    return draft


async def get_draft_by_form_type(user_id: UUID, form_type: str, db: AsyncSession) -> DraftSession | None:
    result = await db.execute(
        select(DraftSession).where(
            DraftSession.user_id == user_id,
            DraftSession.form_type == form_type,
        )
    )
    return result.scalar_one_or_none()


async def delete_draft(draft_id: UUID, user_id: UUID, db: AsyncSession) -> None:
    """
    ลบ DraftSession พร้อม Attachment ทั้งหมดที่ยังผูกกับ draft นี้
    (Attachment ที่ migrate ไปแล้วหลัง submit จะไม่ถูกแตะ เพราะ application_id เปลี่ยนไปแล้ว)
    """
    result = await db.execute(
        select(DraftSession).where(
            DraftSession.id == draft_id,
            DraftSession.user_id == user_id,
        )
    )
    draft = result.scalar_one_or_none()
    if not draft:
        raise NotFoundError("ไม่พบ draft")

    # 1. ลบ Attachment (disk + DB) ที่ยังผูกกับ draft นี้
    await _delete_attachments_for(draft_id, db)

    # 2. ลบ DraftSession
    await db.delete(draft)
    await db.commit()
    logger.info(f"Draft {draft_id} deleted by user {user_id}")


async def update_draft(
    draft_id: UUID,
    user_id: UUID,
    data_dict: dict,
    db: AsyncSession,
) -> DraftSession:
    result = await db.execute(
        select(DraftSession).where(
            DraftSession.id == draft_id,
            DraftSession.user_id == user_id,
        )
    )
    draft = result.scalar_one_or_none()
    if not draft:
        raise NotFoundError("ไม่พบ draft")

    if "form_data" in data_dict and data_dict["form_data"] is not None:
        draft.form_data = data_dict["form_data"]
    if "current_step" in data_dict and data_dict["current_step"] is not None:
        draft.current_step = data_dict["current_step"]

    await db.commit()
    await db.refresh(draft)
    return draft
