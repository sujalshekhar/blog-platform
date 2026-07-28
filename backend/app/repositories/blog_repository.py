from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.blog import Blog
from app.enums.blog_status import BlogStatus

class BlogRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active_by_group_id(self, group_id: int) -> Optional[Blog]:
        return (
            self.db.query(Blog)
            .filter(Blog.blog_group_id == group_id, Blog.is_active_version == True)
            .first()
        )

    def get_all_active_approved(self, skip: int = 0, limit: int = 100) -> List[Blog]:
        return (
            self.db.query(Blog)
            .filter(Blog.is_active_version == True, Blog.status == BlogStatus.APPROVED)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_all_active_by_author(self, author_id: int, skip: int = 0, limit: int = 100) -> List[Blog]:
        return (
            self.db.query(Blog)
            .filter(Blog.is_active_version == True, Blog.author_id == author_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_drafts_by_author(self, author_id: int, skip: int = 0, limit: int = 100) -> List[Blog]:
        return (
            self.db.query(Blog)
            .filter(Blog.is_active_version == True, Blog.author_id == author_id, Blog.status == BlogStatus.DRAFT)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_history_by_group_id(self, group_id: int) -> List[Blog]:
        return (
            self.db.query(Blog)
            .filter(Blog.blog_group_id == group_id)
            .order_by(Blog.version.desc())
            .all()
        )


    def get_all_active(self, skip: int = 0, limit: int = 100) -> List[Blog]:
        # For admin/approver to see all active blogs, including pending
        return (
            self.db.query(Blog)
            .filter(Blog.is_active_version == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_version(self, blog: Blog) -> Blog:
        self.db.add(blog)
        self.db.commit()
        self.db.refresh(blog)
        return blog

    def mark_inactive(self, group_id: int):
        self.db.query(Blog).filter(Blog.blog_group_id == group_id).update({"is_active_version": False})
        self.db.commit()

