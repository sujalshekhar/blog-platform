import redis
from app.core.config import settings
from app.core.logger import logger

# Global Redis client
try:
    redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception as e:
    logger.error(f"Failed to initialize Redis client: {e}")
    redis_client = None

def get_redis():
    """Dependency or helper to get the redis client."""
    return redis_client

def invalidate_blog_cache(blog_id: int):
    """
    Invalidates the cache for a specific blog.
    Should be called whenever a blog is created, updated, approved, or deleted.
    """
    if redis_client:
        try:
            cache_key = f"blog:{blog_id}"
            deleted = redis_client.delete(cache_key)
            if deleted:
                logger.info(f"Invalidated cache for blog {blog_id}")
        except Exception as e:
            logger.error(f"Failed to invalidate cache for blog {blog_id}: {e}")

