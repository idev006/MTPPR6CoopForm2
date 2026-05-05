import uuid
from typing import List, Optional
from sqlalchemy import select, update, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification
from loguru import logger

class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_notification(
        self,
        user_id: uuid.UUID,
        title: str,
        message: str,
        type: str = "info",
        link: Optional[str] = None
    ) -> Notification:
        """
        Create a new notification for a user.
        """
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            link=link
        )
        self.db.add(notif)
        await self.db.commit()
        await self.db.refresh(notif)
        logger.info(f"Notification created for user {user_id}: {title}")
        return notif

    async def get_user_notifications(
        self, 
        user_id: uuid.UUID | str, 
        limit: int = 50,
        unread_only: bool = False
    ) -> List[Notification]:
        """
        Get latest notifications for a user.
        """
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)

        stmt = select(Notification).where(Notification.user_id == user_id)

        if unread_only:
            stmt = stmt.where(Notification.is_read == False)

        stmt = stmt.order_by(desc(Notification.created_at)).limit(limit)
            
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def mark_as_read(self, notification_id: uuid.UUID | str, user_id: uuid.UUID | str | None = None):
        """
        Mark a specific notification as read.
        If user_id is provided, only mark if the notification belongs to that user.
        """
        if isinstance(notification_id, str):
            notification_id = uuid.UUID(notification_id)

        stmt = update(Notification).where(Notification.id == notification_id)
        if user_id is not None:
            if isinstance(user_id, str):
                user_id = uuid.UUID(user_id)
            stmt = stmt.where(Notification.user_id == user_id)
        stmt = stmt.values(is_read=True)
        await self.db.execute(stmt)
        await self.db.commit()

    async def mark_all_as_read(self, user_id: uuid.UUID | str):
        """
        Mark all notifications for a user as read.
        """
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)

        stmt = update(Notification).where(Notification.user_id == user_id).values(is_read=True)
        await self.db.execute(stmt)
        await self.db.commit()
