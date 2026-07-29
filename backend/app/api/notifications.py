from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.repositories.notification_repository import NotificationRepository

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)

@router.get("/", response_model=List[NotificationResponse])
def get_notifications(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = NotificationRepository(db)
    notifications = repo.get_by_user_id(current_user.id, skip, limit)
    return [NotificationResponse.model_validate(n) for n in notifications]

@router.put("/{notification_id}/read", status_code=status.HTTP_200_OK)
def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = NotificationRepository(db)
    
    # Optional: Verify notification belongs to user before marking read
    from app.models.notification import Notification
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    success = repo.mark_as_read(notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"status": "success"}
