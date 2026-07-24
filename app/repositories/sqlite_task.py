from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Any
from app.core.sqlite_db import get_sqlite_conn, DEFAULT_DB_PATH
from app.domain.entities import Task

class SQLiteTaskRepository:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self.db_path = db_path

    @contextmanager
    def _get_cursor(self) -> Generator[Any, None, None]:
        """Context manager helper to provide a cursor and handle connection cleanup."""
        with get_sqlite_conn(self.db_path) as conn:
            yield conn.cursor()

    @staticmethod
    def _to_task(row: Any) -> Task:
        """Map SQLite row to Task entity."""
        return Task(
            id=row["id"],
            title=row["title"],
            done=bool(row["done"])
        )

    def list_all(self) -> list[Task]:
        with self._get_cursor() as cursor:
            cursor.execute("SELECT id, title, done FROM tasks ORDER BY id ASC")
            return [self._to_task(row) for row in cursor.fetchall()]

    def find_by_id(self, task_id: int) -> Task | None:
        with self._get_cursor() as cursor:
            cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            return self._to_task(row) if row else None