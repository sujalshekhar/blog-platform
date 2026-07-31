from sqlalchemy.orm import Session
from app.repositories.chat_repository import ChatRepository
from app.repositories.blog_repository import BlogRepository
from app.schemas.chat import MessageResponse
from app.enums.blog_status import BlogStatus
from fastapi import HTTPException
from app.constants import messages

class ChatService:
    """Service layer for chat-related business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = ChatRepository(db)
        self.blog_repo = BlogRepository(db)

    def _ensure_blog_is_public(self, blog_group_id: int):
        """
        Validates that a blog exists and is publicly accessible (APPROVED).
        
        Args:
            blog_group_id (int): The group ID of the blog to check.
            
        Raises:
            HTTPException (404): If the blog does not exist.
            HTTPException (403): If the blog is not in an APPROVED state.
        """
        blog = self.blog_repo.get_active_by_group_id(blog_group_id)
        if not blog:
            raise HTTPException(status_code=404, detail=messages.ERR_BLOG_NOT_FOUND)
        if blog.status != BlogStatus.APPROVED:
            raise HTTPException(status_code=403, detail=messages.ERR_CHAT_NOT_PUBLIC)

    def get_chat_history(self, blog_group_id: int, cursor: int = None, limit: int = 50):
        """
        Fetches chronologically ordered message history for a public blog's chat.
        Uses cursor-based pagination for highly efficient real-time scrolling.
        
        Args:
            blog_group_id (int): The ID of the blog.
            cursor (int, optional): The ID of the last fetched message to paginate from.
            limit (int): The maximum number of messages to return.
            
        Returns:
            List[MessageResponse]: A list of formatted chat messages.
        """
        self._ensure_blog_is_public(blog_group_id)
        msgs = self.repo.get_messages_for_blog(blog_group_id, cursor, limit)
        return [MessageResponse.model_validate(m) for m in msgs]

    def save_message(self, blog_group_id: int, author_id: int, content: str) -> MessageResponse:
        """
        Saves a new chat message for a public blog to the database.
        
        Args:
            blog_group_id (int): The ID of the blog where the message is posted.
            author_id (int): The ID of the user sending the message.
            content (str): The actual text content of the message.
            
        Returns:
            MessageResponse: The newly created message.
        """
        self._ensure_blog_is_public(blog_group_id)
        chat = self.repo.get_or_create_chat(blog_group_id)
        msg = self.repo.add_message(chat.id, author_id, content)
        return MessageResponse.model_validate(msg)
