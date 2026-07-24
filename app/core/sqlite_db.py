import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path("tasks.db")

def get_sqlite_conn(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_sqlite_db(db_path: Path = DEFAULT_DB_PATH):
    """
    Creates tasks.db, creates the tasks table if not existing,
    and seeds 3 example tasks if and only if the tasks table is empty.
    """
    with get_sqlite_conn(db_path) as conn:
        cursor = conn.cursor()
        
        # Create table if it does not already exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
        """)
        
        # Count rows first
        cursor.execute("SELECT COUNT(*) FROM tasks")
        count = cursor.fetchone()[0]
        
        # Seed three example tasks ONLY when count is 0
        if count == 0:
            example_tasks = [
                ("Buy groceries", 0),
                ("Read a book", 0),
                ("Learn SQLite", 1)
            ]
            cursor.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                example_tasks
            )
            conn.commit()
