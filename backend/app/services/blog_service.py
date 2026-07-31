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
from app.constants import messages, notifications

class BlogService:
    """
    Service layer for blog content management.
    
    Handles business logic for creating, retrieving, updating, and deleting blogs,
    as well as managing blog approval workflows and caching.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = BlogRepository(db)

    def create_blog(self, user: User, data: BlogCreate) -> BlogResponse:
        """
        Creates a new draft blog for the specified user.

        Args:
            user (User): The author creating the blog.
            data (BlogCreate): The blog creation payload.

        Returns:
            BlogResponse: The newly created draft blog object.
        """
        blog = Blog(
            blog_group_id=0, # temporary, will update
            version=1,
            title=data.title,
            content=data.content,
            cover_image_url=data.cover_image_url,
            blog_type=data.blog_type,
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
        """
        Fetches the active version of a blog by its group ID, utilizing Redis cache-aside pattern.

        Args:
            blog_id (int): The unique group ID of the blog.

        Returns:
            BlogResponse: The requested blog object.

        Raises:
            HTTPException (404): If the blog is not found.
        """
        from app.core.redis_client import redis_client
        from app.core.config import settings
        from app.core.logger import logger

        cache_key = f"blog:{blog_id}"
        
        # 1. Try to fetch from Redis
        if redis_client:
            try:
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    logger.info(f"Cache hit for blog {blog_id}")
                    return BlogResponse.model_validate_json(cached_data)
            except Exception as e:
                logger.error(f"Redis get error for {cache_key}: {e}")

        # 2. Cache miss, fetch from DB
        logger.info(f"Cache miss for blog {blog_id}, querying database.")
        blog = self.repo.get_active_by_group_id(blog_id)
        if not blog:
            raise HTTPException(status_code=404, detail=messages.ERR_BLOG_NOT_FOUND)
            
        response = BlogResponse.model_validate(blog)
        
        # 3. Store in Redis
        if redis_client:
            try:
                redis_client.setex(
                    cache_key, 
                    settings.REDIS_TTL, 
                    response.model_dump_json()
                )
            except Exception as e:
                logger.error(f"Redis set error for {cache_key}: {e}")
                
        return response

    def list_approved_blogs(self, skip: int = 0, limit: int = 100, search: Optional[str] = None, blog_type: Optional[str] = None, sort_by: Optional[str] = None, sort_order: Optional[str] = None) -> List[BlogResponse]:
        """Fetch all approved active blogs, with optional filters and sorting."""
        blogs = self.repo.get_all_active_approved(skip, limit, search, blog_type, sort_by, sort_order)
        return [BlogResponse.model_validate(b) for b in blogs]

    def list_all_active_blogs(self, skip: int = 0, limit: int = 100) -> List[BlogResponse]:
        """Fetch all active blogs regardless of status."""
        blogs = self.repo.get_all_active(skip, limit)
        return [BlogResponse.model_validate(b) for b in blogs]

    def list_my_blogs(self, user_id: int, skip: int = 0, limit: int = 100) -> List[BlogResponse]:
        """Fetch all non-draft active blogs authored by the user."""
        blogs = self.repo.get_all_active_by_author(user_id, skip, limit)
        return [BlogResponse.model_validate(b) for b in blogs]

    def list_my_drafts(self, user_id: int, skip: int = 0, limit: int = 100) -> List[BlogResponse]:
        """Fetch all draft blogs authored by the user."""
        blogs = self.repo.get_drafts_by_author(user_id, skip, limit)
        return [BlogResponse.model_validate(b) for b in blogs]

    def get_blog_history(self, blog_id: int) -> List[BlogResponse]:
        """Fetch all versions of a specific blog group."""
        blogs = self.repo.get_history_by_group_id(blog_id)
        return [BlogResponse.model_validate(b) for b in blogs]

    def update_blog(self, blog_id: int, user: User, data: BlogUpdate) -> BlogResponse:
        """
        Creates a new version of an existing blog and marks the old one as inactive.

        Implements version control by never overwriting blog data. Instead, it creates 
        a completely new row in the database with `version + 1` and updates the 
        `is_active_version` flags transactionally.

        Args:
            blog_id (int): The group ID of the blog to update.
            user (User): The author attempting to update the blog.
            data (BlogUpdate): The new blog content.

        Returns:
            BlogResponse: The newly created active version of the blog.

        Raises:
            HTTPException (404): If the blog is not found.
            HTTPException (403): If the user is not the author.
        """
        blog = self.repo.get_active_by_group_id(blog_id)
        if not blog:
            raise HTTPException(status_code=404, detail=messages.ERR_BLOG_NOT_FOUND)
            
        if blog.author_id != user.id:
            raise HTTPException(status_code=403, detail=messages.ERR_UNAUTHORIZED_UPDATE)

        self.repo.mark_inactive(blog_id)

        new_blog = Blog(
            blog_group_id=blog_id,
            version=blog.version + 1,
            title=data.title,
            content=data.content,
            cover_image_url=data.cover_image_url,
            blog_type=data.blog_type,
            status=BlogStatus.DRAFT,
            author_id=user.id,
            is_active_version=True
        )
        new_version = self.repo.create_version(new_blog)
        
        self.db.commit()
        self.db.refresh(new_version)
        
        from app.core.redis_client import invalidate_blog_cache
        invalidate_blog_cache(blog_id)
        
        return BlogResponse.model_validate(new_version)

    def submit_blog(self, blog_id: int, user: User, background_tasks: BackgroundTasks) -> BlogResponse:
        """
        Submits a draft blog for admin approval and dispatches notifications.

        Updates the blog status to PENDING. Creates notifications for all ADMIN
        and APPROVER users using bulk inserts. Dispatches a background task to
        broadcast the new submission via WebSockets.

        Args:
            blog_id (int): The group ID of the draft blog.
            user (User): The author submitting the blog.
            background_tasks (BackgroundTasks): FastAPI background tasks manager.

        Returns:
            BlogResponse: The updated blog object.

        Raises:
            HTTPException (404): If the blog is not found.
            HTTPException (403): If the user is not the author.
            HTTPException (400): If the blog is not in DRAFT status.
        """
        blog = self.repo.get_active_by_group_id(blog_id)
        if not blog:
            raise HTTPException(status_code=404, detail=messages.ERR_BLOG_NOT_FOUND)
        if blog.author_id != user.id:
            raise HTTPException(status_code=403, detail=messages.ERR_UNAUTHORIZED_SUBMIT)
        if blog.status != BlogStatus.DRAFT:
            raise HTTPException(status_code=400, detail=messages.ERR_ONLY_DRAFT_SUBMIT)
            
        blog.status = BlogStatus.PENDING
        
        user_repo = UserRepository(self.db)
        notif_repo = NotificationRepository(self.db)
        
        admins_and_approvers = user_repo.get_by_roles([UserRole.ADMIN, UserRole.APPROVER])
        
        message_data = {
            "title": notifications.NOTIF_TITLE_NEW_SUBMISSION,
            "message": notifications.notif_msg_new_submission(blog.title, user.first_name),
            "blog_id": blog.blog_group_id
        }
        
        new_notifications = []
        for u in admins_and_approvers:
            new_notifications.append(
                Notification(
                    user_id=u.id,
                    type=NotificationType.BLOG_PENDING,
                    content=json.dumps(message_data),
                )
            )
            
        notif_repo.bulk_create(new_notifications)
        
        self.db.commit()
        self.db.refresh(blog)
            
        background_tasks.add_task(
            manager.broadcast_to_roles, 
            message_data, 
            [UserRole.ADMIN, UserRole.APPROVER]
        )
        
        from app.core.redis_client import invalidate_blog_cache
        invalidate_blog_cache(blog_id)
        
        return BlogResponse.model_validate(blog)

    def approve_blog(self, blog_id: int, approver: User, background_tasks: BackgroundTasks) -> BlogResponse:
        """
        Approves a pending blog and notifies the author.

        Args:
            blog_id (int): The group ID of the blog to approve.
            approver (User): The admin/approver executing this action.
            background_tasks (BackgroundTasks): FastAPI background tasks manager.

        Returns:
            BlogResponse: The updated, approved blog.

        Raises:
            HTTPException (404): If the blog is not found.
        """
        blog = self.repo.get_active_by_group_id(blog_id)
        if not blog:
            raise HTTPException(status_code=404, detail=messages.ERR_BLOG_NOT_FOUND)
            
        blog.status = BlogStatus.APPROVED
        blog.approved_by = approver.id
        blog.approved_at = datetime.now(timezone.utc)
        
        notif_repo = NotificationRepository(self.db)
        message_data = {
            "title": notifications.NOTIF_TITLE_BLOG_APPROVED,
            "message": notifications.notif_msg_blog_approved(blog.title),
            "blog_id": blog.blog_group_id
        }
        notif = Notification(
            user_id=blog.author_id,
            type=NotificationType.BLOG_APPROVED,
            content=json.dumps(message_data),
        )
        notif_repo.create(notif)
        
        self.db.commit()
        self.db.refresh(blog)
        
        background_tasks.add_task(
            manager.send_personal_message,
            message_data,
            blog.author_id
        )
        
        from app.core.redis_client import invalidate_blog_cache
        invalidate_blog_cache(blog_id)
        
        return BlogResponse.model_validate(blog)

    def reject_blog(self, blog_id: int, approver: User, background_tasks: BackgroundTasks) -> BlogResponse:
        """Reject a pending blog and notify its author."""
        blog = self.repo.get_active_by_group_id(blog_id)
        if not blog:
            raise HTTPException(status_code=404, detail=messages.ERR_BLOG_NOT_FOUND)
            
        blog.status = BlogStatus.REJECTED
        blog.approved_by = approver.id
        blog.approved_at = datetime.now(timezone.utc)
        
        notif_repo = NotificationRepository(self.db)
        message_data = {
            "title": notifications.NOTIF_TITLE_BLOG_REJECTED,
            "message": notifications.notif_msg_blog_rejected(blog.title),
            "blog_id": blog.blog_group_id
        }
        notif = Notification(
            user_id=blog.author_id,
            type=NotificationType.BLOG_REJECTED,
            content=json.dumps(message_data),
        )
        notif_repo.create(notif)
        
        self.db.commit()
        self.db.refresh(blog)
        
        background_tasks.add_task(
            manager.send_personal_message,
            message_data,
            blog.author_id
        )
        
        from app.core.redis_client import invalidate_blog_cache
        invalidate_blog_cache(blog_id)
        
        return BlogResponse.model_validate(blog)

    def delete_blog(self, blog_id: int, user: User):
        """Soft-delete a blog by marking all its versions inactive."""
        blog = self.repo.get_active_by_group_id(blog_id)
        if not blog:
            raise HTTPException(status_code=404, detail=messages.ERR_BLOG_NOT_FOUND)
            
        if blog.author_id != user.id and user.role not in [UserRole.ADMIN, UserRole.APPROVER]:
            raise HTTPException(status_code=403, detail=messages.ERR_UNAUTHORIZED_DELETE)
            
        self.repo.mark_inactive(blog_id)
        self.db.commit()
        
        from app.core.redis_client import invalidate_blog_cache
        invalidate_blog_cache(blog_id)
