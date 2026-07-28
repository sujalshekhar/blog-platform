from enum import Enum

class UserRole(str, Enum):
    """
    Enum representing different user access roles in the platform.
    Using string enum subclasses for straightforward JSON and DB serialization.
    """
    USER = "USER"
    APPROVER = "APPROVER"
    ADMIN = "ADMIN"
