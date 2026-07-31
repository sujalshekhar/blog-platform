from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.enums.feature_status import FeatureStatus

class FeatureRequestCreate(BaseModel):
    title: str
    description: str
    priority: Optional[int] = 3
    category: Optional[str] = None

class FeatureRequestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    category: Optional[str] = None

class FeatureRequestStatusUpdate(BaseModel):
    status: FeatureStatus

class FeatureRequestResponse(BaseModel):
    id: int
    title: str
    description: str
    status: FeatureStatus
    priority: int
    category: Optional[str]
    requested_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
