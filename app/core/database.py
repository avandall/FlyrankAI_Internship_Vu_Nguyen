import asyncpg
from app.core.config import settings

class Database:
    def __init__(self):
        self.pool: asyncpg.Pool | None = None

    async def connect(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(dsn=settings.DATABASE_URL, timeout=2.0, command_timeout=2.0)


    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            self.pool = None

db = Database()
