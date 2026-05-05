from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.core.dependencies import CurrentUser, DbSession
from app.services.notification_service import NotificationService
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class NotificationRead(BaseModel):
    id: UUID
    title: str
    message: str
    type: str
    is_read: bool
    link: str | None
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=List[NotificationRead])
async def list_my_notifications(
    db: DbSession,
    current_user: CurrentUser,
    unread_only: bool = False
):
    service = NotificationService(db)
    return await service.get_user_notifications(current_user["id"], unread_only=unread_only)

@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    service = NotificationService(db)
    await service.mark_as_read(notification_id, user_id=current_user["id"])
    return {"status": "success"}

@router.post("/read-all")
async def mark_all_notifications_read(
    db: DbSession,
    current_user: CurrentUser
):
    service = NotificationService(db)
    await service.mark_all_as_read(current_user["id"])
    return {"status": "success"}
