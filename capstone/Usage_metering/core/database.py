import asyncpg
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Global connection pool
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
    p = await get_db_pool()
    async with p.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS tenants (
            tenant_id       TEXT PRIMARY KEY,
            name            TEXT NOT NULL,
            email           TEXT,
            plan            TEXT DEFAULT 'free',
            stripe_customer_id TEXT,
            stripe_subscription_id TEXT,
            subscription_status TEXT DEFAULT 'active',
            plan_period_start TIMESTAMP,
            plan_period_end TIMESTAMP,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS usage_events (
            event_id        TEXT PRIMARY KEY,
            idempotency_key TEXT NOT NULL UNIQUE,
            tenant_id       TEXT NOT NULL,
            event_type      TEXT NOT NULL,
            quantity        INTEGER NOT NULL,
            token_type      TEXT,
            cost_micro_cents INTEGER DEFAULT 0,
            metadata        TEXT DEFAULT '{}',
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS billing_periods (
            period_id       TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            period_start    TIMESTAMP NOT NULL,
            period_end      TIMESTAMP NOT NULL,
            total_api_calls INTEGER DEFAULT 0,
            total_ai_tokens INTEGER DEFAULT 0,
            total_cost_micro_cents INTEGER DEFAULT 0,
            invoice_status  TEXT DEFAULT 'pending',
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS stripe_events (
            stripe_event_id TEXT PRIMARY KEY,
            event_type      TEXT NOT NULL,
            payload         TEXT,
            processed       BOOLEAN DEFAULT FALSE,
            processed_at    TIMESTAMP,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
