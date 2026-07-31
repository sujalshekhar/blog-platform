from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse
from app.repositories.notification_repository import NotificationRepository

class NotificationService:
    """Service layer for handling notification-related business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = NotificationRepository(db)

    def get_notifications(self, user_id: int, skip: int = 0, limit: int = 50) -> List[NotificationResponse]:
        """Fetch notifications for a specific user."""
        notifications = self.repo.get_by_user_id(user_id, skip, limit)
        return [NotificationResponse.model_validate(n) for n in notifications]

    def mark_as_read(self, notification_id: int, user: User) -> dict:
        """Mark a notification as read after verifying ownership."""
        notification = self.repo.get_by_id(notification_id)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        if notification.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        notification.is_read = True
        self.db.commit()
            
        return {"status": "success"}
