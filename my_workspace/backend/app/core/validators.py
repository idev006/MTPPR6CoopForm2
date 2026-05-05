from abc import ABC, abstractmethod
from typing import Any, List
from fastapi import HTTPException, status
from loguru import logger

# Magic bytes สำหรับแต่ละประเภทไฟล์ที่อนุญาต
_ALLOWED_MAGIC: list[tuple[bytes, str]] = [
    (b'\x25\x50\x44\x46', 'PDF'),   # %PDF
    (b'\xff\xd8\xff',     'JPEG'),  # JPEG/JPG
    (b'\x89\x50\x4e\x47', 'PNG'),   # \x89PNG
]

class BaseValidator(ABC):
    """
    Interface for all validators.
    """
    @abstractmethod
    def validate(self, data: Any):
        pass

class ValidationPipeline:
    """
    Executes a list of validators in order.
    """
    def __init__(self, validators: List[BaseValidator]):
        self.validators = validators
        from app.core.config import get_validation_config
        self.config = get_validation_config()

    def execute(self, data: Any):
        if not self.config.get("enabled", True):
            logger.warning("Validation is DISABLED globally by Master Switch.")
            return

        for validator in self.validators:
            # Check if this specific validator type is enabled
            v_type = type(validator).__name__
            if v_type == "FileSizeValidator" and not self.config.get("check_file_size", True): continue
            if v_type == "FileTypeValidator" and not self.config.get("check_file_type", True): continue
            if v_type == "AppStatusValidator" and not self.config.get("check_app_status", True): continue
            
            validator.validate(data)

# --- Concrete Validators ---

class FileSizeValidator(BaseValidator):
    def __init__(self, max_mb: int):
        self.max_bytes = max_mb * 1024 * 1024
        self.max_mb = max_mb

    def validate(self, file_size: int):
        if file_size > self.max_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ขนาดไฟล์ใหญ่เกินกำหนด (สูงสุด {self.max_mb} MB)"
            )

class FileTypeValidator(BaseValidator):
    def __init__(self, allowed_mimes: List[str]):
        self.allowed_mimes = allowed_mimes

    def validate(self, mime_type: str):
        if mime_type not in self.allowed_mimes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"รองรับเฉพาะไฟล์ประเภท {', '.join(self.allowed_mimes)} เท่านั้น"
            )

class MagicBytesValidator(BaseValidator):
    """ตรวจสอบ magic bytes จริงของไฟล์ ไม่ใช่แค่ extension หรือ content-type"""

    def validate(self, header: bytes):
        for magic, label in _ALLOWED_MAGIC:
            if header[:len(magic)] == magic:
                return  # valid
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ประเภทไฟล์ไม่ถูกต้อง รองรับเฉพาะ PDF, JPG, PNG เท่านั้น"
        )


class AppStatusValidator(BaseValidator):
    def __init__(self, allowed_statuses: List[str]):
        self.allowed_statuses = allowed_statuses

    def validate(self, current_status: str):
        if current_status not in self.allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ไม่สามารถดำเนินการได้ เนื่องจากสถานะปัจจุบันคือ {current_status}"
            )
