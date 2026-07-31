from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class UserInfo(BaseModel):
    id: int
    first_name: str
    last_name: str
    
    model_config = ConfigDict(from_attributes=True)

class MessageResponse(BaseModel):
    id: int
    chat_id: int
    author_id: int
    content: str
    created_at: datetime
    author: UserInfo

    model_config = ConfigDict(from_attributes=True)

class ChatResponse(BaseModel):
    id: int
    blog_group_id: int
    messages: List[MessageResponse]

    model_config = ConfigDict(from_attributes=True)
