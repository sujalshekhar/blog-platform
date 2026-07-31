from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.feature_request import FeatureRequest
from app.enums.feature_status import FeatureStatus

class FeatureRequestRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, feature_request: FeatureRequest) -> FeatureRequest:
        self.db.add(feature_request)
        self.db.flush()
        return feature_request

    def get_by_id(self, request_id: int) -> Optional[FeatureRequest]:
        return self.db.query(FeatureRequest).filter(FeatureRequest.id == request_id).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[FeatureRequest]:
        return self.db.query(FeatureRequest).order_by(FeatureRequest.created_at.desc()).offset(skip).limit(limit).all()

    def list_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[FeatureRequest]:
        return self.db.query(FeatureRequest).filter(FeatureRequest.requested_by == user_id).order_by(FeatureRequest.created_at.desc()).offset(skip).limit(limit).all()

    def update_status(self, request_id: int, status: FeatureStatus) -> Optional[FeatureRequest]:
        req = self.get_by_id(request_id)
        if req:
            req.status = status
            self.db.flush()
        return req
