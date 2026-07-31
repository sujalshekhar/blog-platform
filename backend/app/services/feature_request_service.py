from typing import List
import json
from fastapi import HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.models.feature_request import FeatureRequest
from app.models.user import User
from app.models.notification import Notification
from app.enums.feature_status import FeatureStatus
from app.enums.role import UserRole
from app.enums.notification_type import NotificationType
from app.schemas.feature_request import FeatureRequestCreate, FeatureRequestResponse
from app.repositories.feature_request_repository import FeatureRequestRepository
from app.repositories.user_repository import UserRepository
from app.repositories.notification_repository import NotificationRepository
from app.sse.manager import manager
from app.constants import messages, notifications

class FeatureRequestService:
    """Service layer for feature request business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = FeatureRequestRepository(db)

    def create_request(self, user: User, data: FeatureRequestCreate, background_tasks: BackgroundTasks) -> FeatureRequestResponse:
        """Create a new feature request and broadcast notification to admins."""
        fr = FeatureRequest(
            title=data.title,
            description=data.description,
            priority=data.priority,
            category=data.category,
            requested_by=user.id,
            status=FeatureStatus.PENDING
        )
        new_fr = self.repo.create(fr)

        user_repo = UserRepository(self.db)
        notif_repo = NotificationRepository(self.db)
        admins = user_repo.get_by_roles([UserRole.ADMIN])

        message_data = {
            "title": notifications.NOTIF_TITLE_NEW_FEATURE,
            "message": notifications.notif_msg_new_feature(new_fr.title, user.first_name),
            "feature_request_id": new_fr.id
        }

        new_notifications = []
        for admin in admins:
            new_notifications.append(
                Notification(
                    user_id=admin.id,
                    type=NotificationType.FEATURE_REQUESTED,
                    content=json.dumps(message_data),
                )
            )
            
        notif_repo.bulk_create(new_notifications)
        
        self.db.commit()
        self.db.refresh(new_fr)
            
        background_tasks.add_task(
            manager.broadcast_to_roles,
            message_data,
            [UserRole.ADMIN]
        )

        return FeatureRequestResponse.model_validate(new_fr)

    def update_status(self, request_id: int, admin: User, new_status: FeatureStatus, background_tasks: BackgroundTasks) -> FeatureRequestResponse:
        """Update the status of a feature request and notify the original requester."""
        fr = self.repo.get_by_id(request_id)
        if not fr:
            raise HTTPException(status_code=404, detail=messages.ERR_FEATURE_REQUEST_NOT_FOUND)

        updated_fr = self.repo.update_status(request_id, new_status)
        if not updated_fr:
            raise HTTPException(status_code=404, detail=messages.ERR_FEATURE_REQUEST_NOT_FOUND)

        notif_repo = NotificationRepository(self.db)
        status_display = new_status.value.capitalize()
        
        message_data = {
            "title": notifications.NOTIF_TITLE_FEATURE_STATUS,
            "message": notifications.notif_msg_feature_status(updated_fr.title, status_display),
            "feature_request_id": updated_fr.id
        }
        
        notif = Notification(
            user_id=updated_fr.requested_by,
            type=NotificationType.FEATURE_UPDATED,
            content=json.dumps(message_data),
        )
        notif_repo.create(notif)
        
        self.db.commit()
        self.db.refresh(updated_fr)

        background_tasks.add_task(
            manager.send_personal_message,
            message_data,
            updated_fr.requested_by
        )

        return FeatureRequestResponse.model_validate(updated_fr)

    def list_requests(self, user: User, skip: int = 0, limit: int = 100) -> List[FeatureRequestResponse]:
        """List feature requests based on user role (Admin sees all, Users see their own)."""
        if user.role == UserRole.ADMIN:
            reqs = self.repo.list_all(skip, limit)
        else:
            reqs = self.repo.list_by_user(user.id, skip, limit)
        
        return [FeatureRequestResponse.model_validate(r) for r in reqs]
