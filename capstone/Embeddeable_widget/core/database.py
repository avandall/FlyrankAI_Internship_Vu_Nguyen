import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / 'widget.db'

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize tables."""
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS tenants (
            tenant_id   TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            api_key     TEXT NOT NULL UNIQUE,
            email       TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS widgets (
            widget_id       TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL REFERENCES tenants(tenant_id),
            name            TEXT NOT NULL,
            form_type       TEXT DEFAULT 'contact',    -- contact|signup|popover
            title           TEXT,
            description     TEXT,
            button_text     TEXT DEFAULT 'Submit',
            allowed_domains TEXT DEFAULT '[]',         -- JSON list
            rate_limit_per_min INTEGER DEFAULT 5,
            webhook_url     TEXT,
            primary_color   TEXT DEFAULT '#38BDF8',
            is_active       INTEGER DEFAULT 1,
            version         INTEGER DEFAULT 1,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS submissions (
            submission_id   TEXT PRIMARY KEY,
            widget_id       TEXT NOT NULL,
            tenant_id       TEXT NOT NULL,
            email           TEXT,
            name            TEXT,
            phone           TEXT,
            message         TEXT,
            custom_fields   TEXT DEFAULT '{}',         -- JSON
            source_origin   TEXT,
            source_ip       TEXT,
            country         TEXT,
            city            TEXT,
            region          TEXT,
            geo_provider    TEXT,
            webhook_status  TEXT DEFAULT 'pending',    -- pending|delivered|failed
            submitted_at    TEXT DEFAULT (datetime('now'))
        );
        """)
        conn.commit()

