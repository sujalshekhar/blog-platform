from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.enums.notification_type import NotificationType

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    type: NotificationType
    content: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
