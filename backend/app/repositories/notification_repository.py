from sqlalchemy.orm import Session
from typing import List
from app.models.notification import Notification

class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, notification: Notification) -> Notification:
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 50) -> List[Notification]:
        return (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def mark_as_read(self, notification_id: int) -> bool:
        notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
        if notification:
            notification.is_read = True
            self.db.commit()
            return True
        return False
