from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.enums.blog_status import BlogStatus
from app.enums.blog_type import BlogType

class BlogBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    cover_image_url: Optional[str] = None
    blog_type: BlogType = BlogType.ARTICLE

class BlogCreate(BlogBase):
    pass

class BlogUpdate(BlogBase):
    pass

class UserSummary(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class BlogResponse(BlogBase):
    id: int
    blog_group_id: int
    version: int
    status: BlogStatus
    author_id: int
    author: Optional[UserSummary] = None
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    is_active_version: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
