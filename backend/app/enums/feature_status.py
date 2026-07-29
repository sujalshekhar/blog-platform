from enum import Enum

class FeatureStatus(str, Enum):
    """
    Enum representing the current state of a requested feature.
    """
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    COMPLETED = "COMPLETED"
