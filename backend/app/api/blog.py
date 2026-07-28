from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import get_current_user, require_roles
from app.models.user import User
from app.enums.role import UserRole
from app.schemas.blog import BlogCreate, BlogUpdate, BlogResponse
from app.services.blog_service import BlogService

router = APIRouter(
    prefix="/blogs",
    tags=["Blogs"],
)

@router.post("/", response_model=BlogResponse, status_code=status.HTTP_201_CREATED)
def create_blog(
    data: BlogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new blog (first version). Auth required."""
    return BlogService(db).create_blog(current_user, data)

@router.get("/", response_model=List[BlogResponse])
def get_approved_blogs(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all active, approved blogs. Publicly accessible."""
    return BlogService(db).list_approved_blogs(skip, limit)

@router.get("/all", response_model=List[BlogResponse])
def get_all_active_blogs(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.APPROVER)),
    db: Session = Depends(get_db)
):
    """List all active blogs (including pending/draft). Required: ADMIN or APPROVER."""
    return BlogService(db).list_all_active_blogs(skip, limit)

@router.get("/my-blogs", response_model=List[BlogResponse])
def get_my_blogs(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all active blogs created by the current user."""
    return BlogService(db).list_my_blogs(current_user.id, skip, limit)

@router.get("/my-drafts", response_model=List[BlogResponse])
def get_my_drafts(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all DRAFT blogs created by the current user."""
    return BlogService(db).list_my_drafts(current_user.id, skip, limit)

@router.get("/{blog_id}", response_model=BlogResponse)
def get_blog(
    blog_id: int,
    db: Session = Depends(get_db)
):
    """Get active version of a blog by its group ID."""
    return BlogService(db).get_blog(blog_id)

@router.put("/{blog_id}", response_model=BlogResponse)
def update_blog(
    blog_id: int,
    data: BlogUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a blog by creating a new version. Must be author."""
    return BlogService(db).update_blog(blog_id, current_user, data)

@router.delete("/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(
    blog_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete a blog (marks all versions inactive). Must be author, approver, or admin."""
    BlogService(db).delete_blog(blog_id, current_user)

@router.post("/{blog_id}/submit", response_model=BlogResponse)
def submit_blog(
    blog_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a DRAFT blog for approval (changes status to PENDING). Must be author."""
    return BlogService(db).submit_blog(blog_id, current_user)

@router.post("/{blog_id}/approve", response_model=BlogResponse)
def approve_blog(
    blog_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.APPROVER)),
    db: Session = Depends(get_db)
):
    """Approve a pending blog. Required: ADMIN or APPROVER."""
    return BlogService(db).approve_blog(blog_id, current_user)

@router.post("/{blog_id}/reject", response_model=BlogResponse)
def reject_blog(
    blog_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.APPROVER)),
    db: Session = Depends(get_db)
):
    """Reject a pending blog. Required: ADMIN or APPROVER."""
    return BlogService(db).reject_blog(blog_id, current_user)

@router.get("/{blog_id}/history", response_model=List[BlogResponse])
def get_blog_history(
    blog_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get history of all versions for a blog."""
    return BlogService(db).get_blog_history(blog_id)
