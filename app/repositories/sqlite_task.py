from pathlib import Path
from app.core.sqlite_db import get_sqlite_conn, DEFAULT_DB_PATH
from app.domain.entities import Task

class SQLiteTaskRepository:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self.db_path = db_path

    def list_all(self) -> list[Task]:
        with get_sqlite_conn(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, done FROM tasks ORDER BY id ASC")
            rows = cursor.fetchall()
            return [
                Task(
                    id=row["id"],
                    title=row["title"],
                    done=bool(row["done"])
                )
                for row in rows
            ]
