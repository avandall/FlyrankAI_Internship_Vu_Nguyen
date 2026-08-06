import asyncio
import asyncpg
import logging
from typing import Optional
from capstone.Embeddeable_widget.core.config import DATABASE_URL

logger = logging.getLogger(__name__)

# Global connection pool
pool: Optional[asyncpg.Pool] = None

async def close_db_pool():
    global pool
    if pool:
        try:
            await pool.close()
        except Exception:
            pass
        pool = None

async def get_db_pool() -> asyncpg.Pool:
    global pool
    loop = asyncio.get_running_loop()
    if pool is not None:
        if getattr(pool, '_loop', None) is not loop or getattr(pool, '_closed', True):
            await close_db_pool()

    if pool is None:
        pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    return pool

async def init_db():
    p = await get_db_pool()
    async with p.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS tenants (
            tenant_id   TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            email       TEXT UNIQUE NOT NULL,
            api_key     TEXT UNIQUE NOT NULL,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS widgets (
            widget_id          TEXT PRIMARY KEY,
            tenant_id          TEXT NOT NULL,
            name               TEXT NOT NULL,
            form_type          TEXT NOT NULL,
            title              TEXT,
            description        TEXT,
            button_text        TEXT,
            allowed_domains    JSONB,
            rate_limit_per_min INTEGER DEFAULT 10,
            webhook_url        TEXT,
            is_active          BOOLEAN DEFAULT TRUE,
            primary_color      TEXT,
            created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
        );

        ALTER TABLE widgets ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

        CREATE TABLE IF NOT EXISTS submissions (
            submission_id  TEXT PRIMARY KEY,
            widget_id      TEXT NOT NULL,
            tenant_id      TEXT NOT NULL,
            email          TEXT,
            name           TEXT,
            phone          TEXT,
            message        TEXT,
            custom_fields  JSONB,
            source_origin  TEXT,
            source_ip      TEXT,
            country        TEXT,
            city           TEXT,
            region         TEXT,
            geo_provider   TEXT,
            webhook_status TEXT,
            submitted_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (widget_id) REFERENCES widgets(widget_id),
            FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
        );

        -- Indexes for tenant isolation and queries
        CREATE INDEX IF NOT EXISTS idx_widgets_tenant ON widgets(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_sub_tenant ON submissions(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_sub_widget ON submissions(widget_id);
        """)
