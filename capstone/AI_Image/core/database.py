import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / 'ai_image.db'

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables on first startup."""
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS images (
            image_id       TEXT PRIMARY KEY,
            filename       TEXT NOT NULL,
            file_size_bytes INTEGER NOT NULL,
            format         TEXT NOT NULL,
            width          INTEGER,
            height         INTEGER,
            subject        TEXT NOT NULL,
            category       TEXT NOT NULL,
            attributes     TEXT,            -- JSON list
            caption        TEXT NOT NULL,
            confidence_score REAL NOT NULL,
            is_flagged     INTEGER DEFAULT 0,
            embedding      TEXT,            -- JSON float list
            created_at     TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS ingest_jobs (
            job_id         TEXT PRIMARY KEY,
            image_id       TEXT,
            status         TEXT DEFAULT 'queued',  -- queued|processing|done|failed
            retries        INTEGER DEFAULT 0,
            ai_cost_micro_usd INTEGER DEFAULT 0,
            error_msg      TEXT,
            created_at     TEXT DEFAULT (datetime('now')),
            updated_at     TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS reviews (
            review_id      TEXT PRIMARY KEY,
            image_id       TEXT,
            post_id        TEXT,
            approved       INTEGER NOT NULL,
            reject_reason  TEXT,
            reviewer       TEXT DEFAULT 'human_editor',
            created_at     TEXT DEFAULT (datetime('now'))
        );
        """)
        conn.commit()

