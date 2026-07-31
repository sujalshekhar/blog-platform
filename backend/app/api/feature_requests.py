from typing import List
from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import get_current_user, require_roles
from app.models.user import User
from app.enums.role import UserRole
from app.enums.feature_status import FeatureStatus
from app.schemas.feature_request import FeatureRequestCreate, FeatureRequestResponse, FeatureRequestStatusUpdate
from app.services.feature_request_service import FeatureRequestService

router = APIRouter(
    prefix="/feature-requests",
    tags=["Feature Requests"],
)

@router.post("/", response_model=FeatureRequestResponse, status_code=status.HTTP_201_CREATED)
def create_feature_request(
    data: FeatureRequestCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit a new feature request. Notifies admins."""
    return FeatureRequestService(db).create_request(current_user, data, background_tasks)

@router.get("/", response_model=List[FeatureRequestResponse])
def get_feature_requests(
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List feature requests. Admins see all; users see their own."""
    return FeatureRequestService(db).list_requests(current_user, skip, limit)

@router.patch("/{request_id}", response_model=FeatureRequestResponse)
def update_feature_request_status(
    request_id: int,
    data: FeatureRequestStatusUpdate,
    background_tasks: BackgroundTasks,
    current_admin: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Update a feature request status. Required: ADMIN. Notifies the requester."""
    return FeatureRequestService(db).update_status(request_id, current_admin, data.status, background_tasks)
