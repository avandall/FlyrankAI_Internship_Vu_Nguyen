import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / 'billing.db'

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS tenants (
            tenant_id       TEXT PRIMARY KEY,
            name            TEXT NOT NULL,
            email           TEXT,
            plan            TEXT DEFAULT 'free',
            stripe_customer_id TEXT,
            stripe_subscription_id TEXT,
            subscription_status TEXT DEFAULT 'active',
            plan_period_start TEXT,
            plan_period_end TEXT,
            created_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS usage_events (
            event_id        TEXT PRIMARY KEY,
            idempotency_key TEXT NOT NULL UNIQUE,
            tenant_id       TEXT NOT NULL,
            event_type      TEXT NOT NULL,      -- api_call | ai_tokens
            quantity        INTEGER NOT NULL,    -- number of units
            token_type      TEXT,               -- input|cached_input|output|reasoning (for AI)
            cost_micro_cents INTEGER DEFAULT 0, -- computed cost
            metadata        TEXT DEFAULT '{}',
            created_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS billing_periods (
            period_id       TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            period_start    TEXT NOT NULL,
            period_end      TEXT NOT NULL,
            total_api_calls INTEGER DEFAULT 0,
            total_ai_tokens INTEGER DEFAULT 0,
            total_cost_micro_cents INTEGER DEFAULT 0,
            invoice_status  TEXT DEFAULT 'pending', -- pending|paid|voided
            created_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS stripe_events (
            stripe_event_id TEXT PRIMARY KEY,
            event_type      TEXT NOT NULL,
            payload         TEXT,
            processed       INTEGER DEFAULT 0,
            processed_at    TEXT,
            created_at      TEXT DEFAULT (datetime('now'))
        );
        """)
        conn.commit()


