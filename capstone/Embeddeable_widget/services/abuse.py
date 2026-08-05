import os
import time
from typing import Tuple, Optional
import redis.asyncio as redis
from capstone.Embeddeable_widget.core.config import RATE_LIMIT_WINDOW_SECS

redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)

class AbuseProtection:
    async def check_rate_limit(self, ip: str, widget_id: str, limit: int) -> Tuple[bool, str]:
        """
        Sliding window rate limiter per (IP, widget_id) using Redis.
        """
        key = f"rate:{widget_id}:{ip}"
        now = time.time()
        window_start = now - RATE_LIMIT_WINDOW_SECS

        # ZREMRANGEBYSCORE key 0 window_start
        # ZADD key now now
        # ZCARD key
        # EXPIRE key window
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

    def check_honeypot(self, honeypot_field: Optional[str]) -> bool:
        """Returns True (is spam) if honeypot field is filled."""
        return bool(honeypot_field and honeypot_field.strip())
