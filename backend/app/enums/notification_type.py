from enum import Enum

class NotificationType(str, Enum):
    """
    Enum representing different kinds of notifications dispatched to users.
    """
    BLOG_PENDING = "BLOG_PENDING"
    BLOG_APPROVED = "BLOG_APPROVED"
    BLOG_REJECTED = "BLOG_REJECTED"
    FEATURE_REQUESTED = "FEATURE_REQUESTED"
    FEATURE_UPDATED = "FEATURE_UPDATED"
