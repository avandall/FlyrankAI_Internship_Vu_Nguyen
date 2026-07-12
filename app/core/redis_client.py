import redis.asyncio as aioredis
from app.core.config import settings

class RedisClient:
    def __init__(self):
        self.client: aioredis.Redis | None = None

    def connect(self):
        if not self.client:
            self.client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    async def disconnect(self):
        if self.client:
            await self.client.close()
            self.client = None

    async def ping(self) -> bool:
        if not self.client:
            return False
        try:
            return await self.client.ping()
        except Exception:
            return False

redis_client = RedisClient()
