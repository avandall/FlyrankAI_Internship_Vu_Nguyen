from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Any
from app.core.sqlite_db import get_sqlite_conn, DEFAULT_DB_PATH
from app.domain.entities import Task

class SQLiteTaskRepository:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self.db_path = db_path

    @contextmanager
    def _get_cursor(self, commit: bool = False) -> Generator[Any, None, None]:
        """Context manager helper to provide a cursor, manage transactions, and clean up connections."""
        with get_sqlite_conn(self.db_path) as conn:
            cursor = conn.cursor()
            yield cursor
            if commit:
                conn.commit()

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
            cursor.execute("SELECT * FROM tasks")
            return [self._to_task(row) for row in cursor.fetchall()]

    def find_by_id(self, task_id: int) -> Task | None:
        with self._get_cursor() as cursor:
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            return self._to_task(row) if row else None

    def create(self, title: str) -> Task:
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (title, 0))
            return Task(id=cursor.lastrowid, title=title, done=False)

    def update(self, task_id: int, title: str, done: bool) -> Task | None:
        with self._get_cursor(commit=True) as cursor:
            cursor.execute(
                "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
                (title, 1 if done else 0, task_id)
            )
            if cursor.rowcount == 0:
                return None
            return Task(id=task_id, title=title, done=done)

    def delete(self, task_id: int) -> bool:
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cursor.rowcount > 0