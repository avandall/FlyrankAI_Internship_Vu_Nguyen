import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / 'multi_platform.db'

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS campaigns (
            campaign_id     TEXT PRIMARY KEY,
            title           TEXT NOT NULL,
            content         TEXT NOT NULL,      -- original blog post
            platforms       TEXT DEFAULT '[]',  -- JSON list
            status          TEXT DEFAULT 'draft',
            image_path      TEXT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS platform_posts (
            post_id         TEXT PRIMARY KEY,
            campaign_id     TEXT NOT NULL,
            platform        TEXT NOT NULL,
            idempotency_key TEXT NOT NULL UNIQUE,
            status          TEXT DEFAULT 'queued',
            caption         TEXT,
            image_variant_path TEXT,
            image_width     INTEGER,
            image_height    INTEGER,
            external_post_id TEXT,
            publish_attempts INTEGER DEFAULT 0,
            last_error      TEXT,
            published_at    TEXT,
            created_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS webhook_events (
            event_id        TEXT PRIMARY KEY,
            post_id         TEXT,
            platform        TEXT,
            event_type      TEXT,
            payload         TEXT,               -- JSON
            signature_valid INTEGER,
            processed       INTEGER DEFAULT 0,
            received_at     TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS platform_tokens (
            token_id        TEXT PRIMARY KEY,
            platform        TEXT NOT NULL UNIQUE,
            encrypted_token TEXT NOT NULL,
            created_at      TEXT DEFAULT (datetime('now'))
        );
        """)
        conn.commit()

