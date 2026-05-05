import os
import uuid
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from loguru import logger

from app.models.attachment import Attachment
from app.core.config import get_settings, get_storage_config
from app.core.validators import FileSizeValidator, FileTypeValidator, MagicBytesValidator, ValidationPipeline

class AttachmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        storage_cfg = get_storage_config()
        self.max_size_mb = storage_cfg.get("max_size_mb", 10)
        self.allowed_mimes = storage_cfg.get("allowed_mimes", ["application/pdf"])
        
        # Base directory for all attachments
        self.base_dir = Path("data/attachments")
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def upload_attachment(
        self, 
        application_id: uuid.UUID, 
        file_type: str, 
        file: UploadFile
    ) -> Attachment:
        """
        Save file to disk and record in DB with strict validation.
        """
        # 1. Pipeline Validation
        # We need to read the file size. file.size is available in modern FastAPI/Starlette
        # or we check it after saving. For better UX, we check it before saving if possible.
        
        # อ่าน header bytes สำหรับ magic bytes check
        header = file.file.read(8)
        file.file.seek(0)

        # วัดขนาดไฟล์
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(0)

        # Magic bytes validation (ก่อน content-type เพราะ client อาจ spoof ได้)
        MagicBytesValidator().validate(header)

        # Content-type + size validation ผ่าน pipeline
        ValidationPipeline([
            FileTypeValidator(self.allowed_mimes),
        ]).execute(file.content_type if file.content_type else "")

        FileSizeValidator(self.max_size_mb).validate(size)

        # 2. ลบไฟล์เก่าของ file_type เดียวกัน (ถ้ามี) เพื่อให้ upload ใหม่แทนที่ได้
        existing = await self.db.execute(
            select(Attachment).where(
                Attachment.application_id == application_id,
                Attachment.file_type == file_type,
            )
        )
        for old in existing.scalars().all():
            old_path = Path(old.storage_path)
            if old_path.exists():
                old_path.unlink()
            await self.db.delete(old)
        await self.db.flush()

        # 3. Prepare directory
        app_dir = self.base_dir / str(application_id)
        app_dir.mkdir(parents=True, exist_ok=True)

        # 3. Generate secure filename
        ext = os.path.splitext(file.filename)[1]
        secure_name = f"{uuid.uuid4()}{ext}"
        storage_path = app_dir / secure_name

        # 3. Save to disk
        try:
            with storage_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            raise RuntimeError("ไม่สามารถบันทึกไฟล์ลงระบบได้")

        # 4. Record to DB
        db_attachment = Attachment(
            application_id=application_id,
            file_type=file_type,
            storage_path=str(storage_path),
            original_filename=file.filename,
            file_size_bytes=storage_path.stat().st_size,
            mime_type=file.content_type
        )
        self.db.add(db_attachment)
        await self.db.commit()
        await self.db.refresh(db_attachment)
        
        logger.info(f"Uploaded {file_type} for app {application_id}: {secure_name}")
        return db_attachment

    async def get_application_attachments(self, application_id: uuid.UUID) -> List[Attachment]:
        stmt = select(Attachment).where(Attachment.application_id == application_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_attachment(self, attachment_id: uuid.UUID) -> Optional[Attachment]:
        stmt = select(Attachment).where(Attachment.id == attachment_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_attachment(self, attachment_id: uuid.UUID):
        attachment = await self.get_attachment(attachment_id)
        if not attachment:
            return

        # 1. Delete from Disk
        p = Path(attachment.storage_path)
        if p.exists():
            p.unlink()

        # 2. Delete from DB
        await self.db.delete(attachment)
        await self.db.commit()
        logger.info(f"Deleted attachment {attachment_id}")
