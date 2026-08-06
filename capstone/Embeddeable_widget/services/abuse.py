import os
import time
import logging
from typing import Tuple, Optional, Dict, List
import redis.asyncio as redis
from capstone.Embeddeable_widget.core.config import RATE_LIMIT_WINDOW_SECS

logger = logging.getLogger(__name__)

# Try initializing Redis client, but keep in-memory fallback ready
try:
    redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)
except Exception:
    redis_client = None

# In-memory sliding window storage: key -> list of timestamps
_in_memory_rate_store: Dict[str, List[float]] = {}


class AbuseProtection:
    async def check_rate_limit(self, ip: str, widget_id: str, limit: int) -> Tuple[bool, str]:
        """
        Sliding window rate limiter per (IP, widget_id).
        Uses Redis if accessible, otherwise falls back to in-memory sliding window.
        """
        key = f"rate:{widget_id}:{ip}"
        now = time.time()
        window_start = now - RATE_LIMIT_WINDOW_SECS

        # 1. Try Redis first
        if redis_client:
            try:
                async with redis_client.pipeline(transaction=True) as pipe:
                    pipe.zremrangebyscore(key, 0, window_start)
                    pipe.zadd(key, {str(now): now})
                    pipe.zcard(key)
                    pipe.expire(key, RATE_LIMIT_WINDOW_SECS)
                    results = await pipe.execute()

                count = results[2]
                if count > limit:
                    return False, f"Rate limit exceeded: {count}/{limit} requests in {RATE_LIMIT_WINDOW_SECS}s window"
                return True, ""
            except Exception as e:
                logger.warning(f"Redis rate limiter unavailable ({e}). Using in-memory rate limiter.")

        # 2. In-memory sliding window fallback
        timestamps = _in_memory_rate_store.get(key, [])
        # Prune expired timestamps
        timestamps = [t for t in timestamps if t > window_start]
        timestamps.append(now)
        _in_memory_rate_store[key] = timestamps

        if len(timestamps) > limit:
            return False, f"Rate limit exceeded: {len(timestamps)}/{limit} requests in {RATE_LIMIT_WINDOW_SECS}s window"
        return True, ""

    def check_honeypot(self, honeypot_field: Optional[str]) -> bool:
        """Returns True (is spam) if honeypot field is filled."""
        return bool(honeypot_field and str(honeypot_field).strip())
