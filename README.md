# FlyrankAI - SQLite Tasks Management API

A FastAPI application backed by a persistent SQLite database (`tasks.db`), demonstrating full CRUD capabilities, Clean Architecture, and direct SQL execution.

## Features & Endpoints

- `GET /tasks`: Fetch all tasks (`SELECT * FROM tasks`)
- `GET /tasks/{id}`: Fetch task by ID (`SELECT * FROM tasks WHERE id = ?`)
- `POST /tasks`: Create a new task (`INSERT INTO tasks (title, done) VALUES (?, ?)`)
- `PUT /tasks/{id}`: Update task title and done status (`UPDATE tasks SET title = ?, done = ? WHERE id = ?`)
- `DELETE /tasks/{id}`: Delete task by ID (`DELETE FROM tasks WHERE id = ?`)

## How to Run

1. Install dependencies and start dev server:
   ```bash
   uv run uvicorn main:app --reload --port 8000
   ```

2. Test endpoints using `curl` or Swagger UI at `http://localhost:8000/docs`.

---

## SQL Direct Query Experiment (Stage 4 Checkpoint)

Experiment executed directly against `tasks.db`:

- **Query Executed**: 
  ```sql
  SELECT COUNT(*) FROM tasks;
  ```
- **Result Output**: 
  Returned `3`, indicating there are exactly 3 tasks stored in the SQLite database file (`tasks.db`).
