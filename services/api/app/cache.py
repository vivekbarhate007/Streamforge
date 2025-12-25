"""Redis caching for performance optimization"""
import redis
import json
from functools import wraps
from typing import Optional
import os

# Redis client (will be None if Redis is not available)
redis_client: Optional[redis.Redis] = None


def init_redis():
    """Initialize Redis connection"""
    global redis_client
    try:
        redis_host = os.getenv("REDIS_HOST", "redis")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=0,
            decode_responses=True,
            socket_connect_timeout=2
        )
        # Test connection
        redis_client.ping()
        return True
    except Exception as e:
        print(f"Redis not available: {e}. Caching disabled.")
        redis_client = None
        return False


def cache_result(ttl: int = 300, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if redis_client is None:
                # Redis not available, call function directly
                return await func(*args, **kwargs)

            # Generate cache key
            cache_key = f"{key_prefix}{func.__name__}:{str(args)}:{str(kwargs)}"

            # Try to get from cache
            try:
                cached = redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception:
                pass  # If cache fails, continue to function call

            # Call function and cache result
            result = await func(*args, **kwargs)

            try:
                redis_client.setex(cache_key, ttl, json.dumps(result, default=str))
            except Exception:
                pass  # If cache fails, continue

            return result
        return wrapper
    return decorator


def clear_cache(pattern: str = "*"):
    """Clear cache entries matching pattern"""
    if redis_client is None:
        return

    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
    except Exception:
        pass
