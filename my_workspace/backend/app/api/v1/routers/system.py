import os
import shutil
from datetime import datetime
from pathlib import Path
from sqlalchemy import func, select

from fastapi import APIRouter

from app.core.config import get_storage_config, get_validation_config, get_settings
from app.core.dependencies import StaffOnly, DbSession

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/config")
async def get_system_config():
    """Expose public config to Frontend (SSOT). Intentionally unauthenticated."""
    storage = get_storage_config()
    validation = get_validation_config()
    return {
        "storage": {
            "max_size_mb": storage.get("max_size_mb"),
            "allowed_mimes": storage.get("allowed_mimes"),
        },
        "validation": {
            "enabled": validation.get("enabled"),
            "check_file_size": validation.get("check_file_size"),
            "check_file_type": validation.get("check_file_type"),
        },
    }


@router.get("/stats")
async def get_system_stats(current_user: StaffOnly, db: DbSession):
    from app.models import LoanApplication, User

    apps_count = await db.scalar(select(func.count(LoanApplication.id)))
    users_count = await db.scalar(select(func.count(User.id)))
    pending_apps = await db.scalar(
        select(func.count(LoanApplication.id)).where(LoanApplication.status == "submitted")
    )

    settings = get_settings()
    attachments_dir = Path(settings.DATA_DIR) / "attachments"
    att_size = 0
    att_count = 0
    if attachments_dir.exists():
        for f in attachments_dir.rglob("*"):
            if f.is_file():
                att_size += f.stat().st_size
                att_count += 1

    return {
        "database": {
            "total_applications": apps_count,
            "total_users": users_count,
            "pending_review": pending_apps,
        },
        "storage": {
            "attachment_count": att_count,
            "attachment_total_size_mb": round(att_size / (1024 * 1024), 2),
        },
        "system": {
            "status": "Healthy",
            "environment": os.getenv("ENVIRONMENT", "production"),
        },
    }


@router.post("/clear-cache")
async def clear_system_cache(current_user: StaffOnly):
    settings = get_settings()
    cache_dir = Path(settings.DATA_DIR) / "generated_pdfs"
    if cache_dir.exists():
        for item in cache_dir.iterdir():
            try:
                if item.is_file() or item.is_symlink():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            except Exception as e:
                return {"success": False, "detail": f"Failed to delete {item}: {e}"}
    return {"success": True, "detail": "Cache cleared successfully"}


@router.post("/backup")
async def trigger_system_backup(current_user: StaffOnly):
    """SQLite dev-only backup. Production should use pg_dump via external scheduler."""
    settings = get_settings()
    db_file = Path(settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "").replace("./", ""))
    backup_dir = Path(settings.DATA_DIR) / "backups"

    if not db_file.exists():
        return {"success": False, "detail": "Database file not found (production uses PostgreSQL)"}

    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"backup_{timestamp}.db"

    try:
        shutil.copy2(db_file, backup_file)
    except Exception as e:
        return {"success": False, "detail": f"Backup failed: {e}"}

    return {"success": True, "detail": f"Backup created: {backup_file}"}
