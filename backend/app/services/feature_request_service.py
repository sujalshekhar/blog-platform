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

class FeatureRequestService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = FeatureRequestRepository(db)

    def create_request(self, user: User, data: FeatureRequestCreate, background_tasks: BackgroundTasks) -> FeatureRequestResponse:
        fr = FeatureRequest(
            title=data.title,
            description=data.description,
            priority=data.priority,
            category=data.category,
            requested_by=user.id,
            status=FeatureStatus.PENDING
        )
        new_fr = self.repo.create(fr)

        # Notify admins
        user_repo = UserRepository(self.db)
        notif_repo = NotificationRepository(self.db)
        admins = user_repo.get_by_roles([UserRole.ADMIN])

        message_data = {
            "title": "New Feature Request",
            "message": f"{user.first_name} requested: '{new_fr.title}'",
            "feature_request_id": new_fr.id
        }

        for admin in admins:
            notif = Notification(
                user_id=admin.id,
                type=NotificationType.FEATURE_REQUESTED,
                content=json.dumps(message_data),
            )
            notif_repo.create(notif)
            
        background_tasks.add_task(
            manager.broadcast_to_roles,
            message_data,
            [UserRole.ADMIN]
        )

        return FeatureRequestResponse.model_validate(new_fr)

    def update_status(self, request_id: int, admin: User, new_status: FeatureStatus, background_tasks: BackgroundTasks) -> FeatureRequestResponse:
        fr = self.repo.get_by_id(request_id)
        if not fr:
            raise HTTPException(status_code=404, detail="Feature request not found")

        updated_fr = self.repo.update_status(request_id, new_status)
        if not updated_fr:
            raise HTTPException(status_code=404, detail="Feature request not found")

        # Notify the original requester
        notif_repo = NotificationRepository(self.db)
        status_display = new_status.value.capitalize()
        
        message_data = {
            "title": f"Feature Request {status_display}",
            "message": f"Your feature request '{updated_fr.title}' is now {status_display}.",
            "feature_request_id": updated_fr.id
        }
        
        notif = Notification(
            user_id=updated_fr.requested_by,
            type=NotificationType.FEATURE_UPDATED,
            content=json.dumps(message_data),
        )
        notif_repo.create(notif)

        background_tasks.add_task(
            manager.send_personal_message,
            message_data,
            updated_fr.requested_by
        )

        return FeatureRequestResponse.model_validate(updated_fr)

    def list_requests(self, user: User, skip: int = 0, limit: int = 100) -> List[FeatureRequestResponse]:
        if user.role == UserRole.ADMIN:
            reqs = self.repo.list_all(skip, limit)
        else:
            reqs = self.repo.list_by_user(user.id, skip, limit)
        
        return [FeatureRequestResponse.model_validate(r) for r in reqs]
