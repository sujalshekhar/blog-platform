from datetime import datetime, timezone
from typing import List, Optional
import json
from fastapi import HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.models.blog import Blog
from app.models.user import User
from app.models.notification import Notification
from app.enums.blog_status import BlogStatus
from app.enums.role import UserRole
from app.enums.notification_type import NotificationType
from app.schemas.blog import BlogCreate, BlogUpdate, BlogResponse
from app.repositories.blog_repository import BlogRepository
from app.repositories.user_repository import UserRepository
from app.repositories.notification_repository import NotificationRepository
from app.sse.manager import manager

class BlogService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = BlogRepository(db)

    def create_blog(self, user: User, data: BlogCreate) -> BlogResponse:
        blog = Blog(
            blog_group_id=0, # temporary, will update
            version=1,
            title=data.title,
            content=data.content,
            cover_image_url=data.cover_image_url,
            status=BlogStatus.DRAFT,
            author_id=user.id,
            is_active_version=True
        )
        new_blog = self.repo.create_version(blog)
        # Update blog_group_id to be its own id for the first version
        new_blog.blog_group_id = new_blog.id
        self.db.commit()
        self.db.refresh(new_blog)
        return BlogResponse.model_validate(new_blog)
        
    def get_blog(self, blog_id: int) -> BlogResponse:
        blog = self.repo.get_active_by_group_id(blog_id)
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found")
        return BlogResponse.model_validate(blog)

    def list_approved_blogs(self, skip: int = 0, limit: int = 100) -> List[BlogResponse]:
        blogs = self.repo.get_all_active_approved(skip, limit)
        return [BlogResponse.model_validate(b) for b in blogs]

    def list_all_active_blogs(self, skip: int = 0, limit: int = 100) -> List[BlogResponse]:
        blogs = self.repo.get_all_active(skip, limit)
        return [BlogResponse.model_validate(b) for b in blogs]

    def list_my_blogs(self, user_id: int, skip: int = 0, limit: int = 100) -> List[BlogResponse]:
        blogs = self.repo.get_all_active_by_author(user_id, skip, limit)
        return [BlogResponse.model_validate(b) for b in blogs]

    def list_my_drafts(self, user_id: int, skip: int = 0, limit: int = 100) -> List[BlogResponse]:
        blogs = self.repo.get_drafts_by_author(user_id, skip, limit)
        return [BlogResponse.model_validate(b) for b in blogs]

    def get_blog_history(self, blog_id: int) -> List[BlogResponse]:
        blogs = self.repo.get_history_by_group_id(blog_id)
        return [BlogResponse.model_validate(b) for b in blogs]

    def update_blog(self, blog_id: int, user: User, data: BlogUpdate) -> BlogResponse:
        blog = self.repo.get_active_by_group_id(blog_id)
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found")
            
        if blog.author_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this blog")

        # Mark current version inactive
        self.repo.mark_inactive(blog_id)

        # Create new version
        new_blog = Blog(
            blog_group_id=blog_id,
            version=blog.version + 1,
            title=data.title,
            content=data.content,
            cover_image_url=data.cover_image_url,
            status=BlogStatus.DRAFT,
            author_id=user.id,
            is_active_version=True
        )
        new_version = self.repo.create_version(new_blog)
        return BlogResponse.model_validate(new_version)

    def submit_blog(self, blog_id: int, user: User, background_tasks: BackgroundTasks) -> BlogResponse:
        blog = self.repo.get_active_by_group_id(blog_id)
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found")
        if blog.author_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to submit this blog")
        if blog.status != BlogStatus.DRAFT:
            raise HTTPException(status_code=400, detail="Only DRAFT blogs can be submitted")
            
        blog.status = BlogStatus.PENDING
        self.db.commit()
        self.db.refresh(blog)
        
        # Notify admins and approvers
        user_repo = UserRepository(self.db)
        notif_repo = NotificationRepository(self.db)
        admins_and_approvers = user_repo.get_by_roles([UserRole.ADMIN, UserRole.APPROVER])
        
        message_data = {
            "title": "New Blog Submission",
            "message": f"'{blog.title}' was submitted for review by {user.first_name}.",
            "blog_id": blog.blog_group_id
        }
        
        for u in admins_and_approvers:
            notif = Notification(
                user_id=u.id,
                type=NotificationType.BLOG_PENDING,
                content=json.dumps(message_data),
            )
            notif_repo.create(notif)
            
        background_tasks.add_task(
            manager.broadcast_to_roles, 
            message_data, 
            [UserRole.ADMIN, UserRole.APPROVER]
        )
        
        return BlogResponse.model_validate(blog)

    def approve_blog(self, blog_id: int, approver: User, background_tasks: BackgroundTasks) -> BlogResponse:
        blog = self.repo.get_active_by_group_id(blog_id)
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found")
            
        blog.status = BlogStatus.APPROVED
        blog.approved_by = approver.id
        blog.approved_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(blog)
        
        # Notify the author
        notif_repo = NotificationRepository(self.db)
        message_data = {
            "title": "Blog Approved",
            "message": f"Your blog '{blog.title}' has been approved!",
            "blog_id": blog.blog_group_id
        }
        notif = Notification(
            user_id=blog.author_id,
            type=NotificationType.BLOG_APPROVED,
            content=json.dumps(message_data),
        )
        notif_repo.create(notif)
        
        background_tasks.add_task(
            manager.send_personal_message,
            message_data,
            blog.author_id
        )
        
        return BlogResponse.model_validate(blog)

    def reject_blog(self, blog_id: int, approver: User, background_tasks: BackgroundTasks) -> BlogResponse:
        blog = self.repo.get_active_by_group_id(blog_id)
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found")
            
        blog.status = BlogStatus.REJECTED
        blog.approved_by = approver.id
        blog.approved_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(blog)
        
        # Notify the author
        notif_repo = NotificationRepository(self.db)
        message_data = {
            "title": "Blog Rejected",
            "message": f"Your blog '{blog.title}' has been rejected.",
            "blog_id": blog.blog_group_id
        }
        notif = Notification(
            user_id=blog.author_id,
            type=NotificationType.BLOG_REJECTED,
            content=json.dumps(message_data),
        )
        notif_repo.create(notif)
        
        background_tasks.add_task(
            manager.send_personal_message,
            message_data,
            blog.author_id
        )
        
        return BlogResponse.model_validate(blog)

    def delete_blog(self, blog_id: int, user: User):
        blog = self.repo.get_active_by_group_id(blog_id)
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found")
            
        if blog.author_id != user.id and user.role not in [UserRole.ADMIN, UserRole.APPROVER]:
            raise HTTPException(status_code=403, detail="Not authorized to delete this blog")
            
        # Soft delete by marking all versions inactive
        self.repo.mark_inactive(blog_id)
