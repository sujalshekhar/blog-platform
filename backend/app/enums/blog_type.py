from enum import Enum

class BlogType(str, Enum):
    ARTICLE = "ARTICLE"
    TUTORIAL = "TUTORIAL"
    NEWS = "NEWS"
    OPINION = "OPINION"
