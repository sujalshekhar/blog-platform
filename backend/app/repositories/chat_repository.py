from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from app.models.chat import Chat
from app.models.message import Message

class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_chat(self, blog_group_id: int) -> Chat:
        chat = self.db.query(Chat).filter(Chat.blog_group_id == blog_group_id).first()
        if not chat:
            chat = Chat(blog_group_id=blog_group_id)
            self.db.add(chat)
            self.db.commit()
            self.db.refresh(chat)
        return chat

    def add_message(self, chat_id: int, author_id: int, content: str) -> Message:
        message = Message(chat_id=chat_id, author_id=author_id, content=content)
        self.db.add(message)
        self.db.commit()
        # Eager load the author so we can serialize it
        message = self.db.query(Message).options(joinedload(Message.author)).filter(Message.id == message.id).first()
        return message

    def get_messages_for_blog(self, blog_group_id: int, cursor: Optional[int] = None, limit: int = 50) -> List[Message]:
        chat = self.db.query(Chat).filter(Chat.blog_group_id == blog_group_id).first()
        if not chat:
            return []
        
        query = self.db.query(Message)\
            .options(joinedload(Message.author))\
            .filter(Message.chat_id == chat.id)
            
        if cursor:
            query = query.filter(Message.id < cursor)
            
        messages = query.order_by(Message.id.desc()).limit(limit).all()
        # Reverse because we fetch descending to get the 'latest' before cursor, 
        # but we want to return them in chronological order.
        return list(reversed(messages))
