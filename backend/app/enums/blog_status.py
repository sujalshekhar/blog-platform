from enum import Enum

class BlogStatus(str, Enum):
    """
    Enum representing the current moderation/editing status of a blog.
    """
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
