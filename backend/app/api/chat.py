from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.chat import MessageResponse
from app.services.chat_service import ChatService
from app.core.logger import logger

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

@router.get("/{blog_group_id}", response_model=List[MessageResponse])
def get_chat_history(
    blog_group_id: int,
    cursor: int = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetch the message history for a public blog's chat.
    
    Supports cursor-based pagination. The client provides the ID of the oldest 
    message it has, and the server returns the next `limit` messages older than that.
    """
    logger.info(f"User {current_user.id} fetching chat history for blog {blog_group_id}, cursor={cursor}")
    return ChatService(db).get_chat_history(blog_group_id, cursor, limit)
