import asyncpg
import logging
from typing import Optional
from capstone.Multi_platform.core.config import DATABASE_URL

logger = logging.getLogger(__name__)

# Global connection pool
pool: Optional[asyncpg.Pool] = None

async def get_db_pool() -> asyncpg.Pool:
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(DATABASE_URL)
    return pool

async def close_db_pool():
    global pool
    if pool:
        await pool.close()
        pool = None

async def init_db():
    p = await get_db_pool()
    async with p.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            campaign_id TEXT PRIMARY KEY,
            title       TEXT,
            content     TEXT,
            platforms   JSONB,
            status      TEXT,
            image_path  TEXT,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS platform_posts (
            post_id            TEXT PRIMARY KEY,
            campaign_id        TEXT,
            platform           TEXT,
            idempotency_key    TEXT UNIQUE,
            status             TEXT,
            caption            TEXT,
            image_variant_path TEXT,
            image_width        INTEGER,
            image_height       INTEGER,
            external_post_id   TEXT,
            publish_attempts   INTEGER DEFAULT 0,
            last_error         TEXT,
            published_at       TIMESTAMP,
            created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(campaign_id) REFERENCES campaigns(campaign_id)
        );

        CREATE TABLE IF NOT EXISTS platform_tokens (
            platform        TEXT PRIMARY KEY,
            encrypted_token TEXT,
            updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS webhook_events (
            event_id        TEXT PRIMARY KEY,
            post_id         TEXT,
            platform        TEXT,
            event_type      TEXT,
            payload         TEXT,
            signature_valid BOOLEAN,
            processed       BOOLEAN DEFAULT FALSE,
            received_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
