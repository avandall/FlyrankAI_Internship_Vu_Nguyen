import asyncpg
import logging
from typing import Optional
from capstone.AI_Image.core.config import DATABASE_URL

logger = logging.getLogger(__name__)

# We'll use a global connection pool
pool: Optional[asyncpg.Pool] = None

async def get_db_pool() -> asyncpg.Pool:
    global pool
    if pool is None:
        db_url = "postgresql://postgres:postgres@localhost:5433/postgres"
        pool = await asyncpg.create_pool(db_url)
    return pool

async def close_db_pool():
    global pool
    if pool:
        await pool.close()
        pool = None

async def init_db():
    """Create tables if not exists using asyncpg."""
    p = await get_db_pool()
    async with p.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS images (
            image_id       TEXT PRIMARY KEY,
            filename       TEXT NOT NULL,
            file_size_bytes INTEGER NOT NULL,
            format         TEXT NOT NULL,
            width          INTEGER,
            height         INTEGER,
            subject        TEXT NOT NULL,
            category       TEXT NOT NULL,
            attributes     JSONB,
            caption        TEXT NOT NULL,
            confidence_score REAL NOT NULL,
            is_flagged     INTEGER DEFAULT 0,
            embedding      JSONB,
            created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS ingest_jobs (
            job_id         TEXT PRIMARY KEY,
            image_id       TEXT,
            status         TEXT DEFAULT 'queued',
            retries        INTEGER DEFAULT 0,
            ai_cost_micro_usd INTEGER DEFAULT 0,
            error_msg      TEXT,
            created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS reviews (
            review_id      TEXT PRIMARY KEY,
            image_id       TEXT,
            post_id        TEXT,
            approved       BOOLEAN NOT NULL,
            reject_reason  TEXT,
            reviewer       TEXT DEFAULT 'human_editor',
            created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
