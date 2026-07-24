# FlyrankAI - SQLite Tasks Management API

A FastAPI application backed by a persistent SQLite database (`tasks.db`), demonstrating full CRUD capabilities, Clean Architecture, and direct SQL execution.

---

## 🚀 Quick Start (One Command)

To run the application on a fresh clone (or after deleting `tasks.db`), run:

```bash
uv run uvicorn main:app --port 8000
```

> **Note**: The application automatically creates the `tasks.db` database file, initializes the `tasks` table schema, and seeds 3 initial tasks on first startup. No manual setup is required!

---

## 💡 Why SQLite Was Chosen

- **Single-File Storage**: The entire database resides in a single, lightweight file (`tasks.db`).
- **Zero Setup**: Uses Python's built-in `sqlite3` standard library — no separate database server or Docker daemon installation is needed to run.
- **Survives Restarts**: Data persists reliably across application restarts, ensuring true database durability.

---

## 📁 Database Location & Setup

- **File Path**: `tasks.db` (located at the root of the project).
- **Auto-Initialization**: Opening/connecting to `tasks.db` on app startup automatically creates the file and schema if it does not exist yet.
- **Version Control (`.gitignore`)**: `tasks.db` is `.gitignore`d so that each developer or stranger who clones the repository gets a clean, fresh database auto-seeded with the 3 default tasks.

---

## 🛠️ API Endpoints (CRUD)

| Method | Endpoint | Description | SQL Query Executed |
| :--- | :--- | :--- | :--- |
| `GET` | `/tasks` | List all tasks | `SELECT * FROM tasks` |
| `GET` | `/tasks/{id}` | Get task by ID | `SELECT * FROM tasks WHERE id = ?` |
| `POST` | `/tasks` | Create a new task | `INSERT INTO tasks (title, done) VALUES (?, ?)` |
| `PUT` | `/tasks/{id}` | Update task title and done status | `UPDATE tasks SET title = ?, done = ? WHERE id = ?` |
| `DELETE` | `/tasks/{id}` | Delete task by ID | `DELETE FROM tasks WHERE id = ?` |

---

## 🏗️ Architecture & Concepts

### 🧪 Storage is Just an Implementation Detail
All endpoint tests written for Assignment 1 pass identically without changing a single line of API contract or router code. Identical tests passing across storage migrations proves that storage is **just an implementation detail** isolated behind repository interfaces in Clean Architecture.

### ⚡ Database Indexing (`idx_tasks_done`)
An index on `tasks(done)` creates a fast search lookup structure that speeds up filtering queries (`SELECT * FROM tasks WHERE done = 1`) by avoiding full table scans.

### 🛡️ Transaction Atomicity
Multi-step database changes (such as seeding the 3 initial tasks) are wrapped in a single database transaction so that either all statements succeed or none do (all-or-nothing), preventing partial data corruption.

---

## 🔍 Database Inspection & Direct SQL Experiment

### DB Browser Screenshot
Below is a screenshot of `tasks.db` opened directly inside **DB Browser for SQLite**:

![DB Browser for SQLite Screenshot](docs/db_browser_screenshot.png)

### Direct SQL Query Executed
Command run directly in DB Browser's **Execute SQL** tab:

```sql
SELECT COUNT(*) FROM tasks;
```

**Result Output**: Returned `3`, confirming there are 3 tasks stored live inside `tasks.db`.

---

## 🤖 AI vs Me: The AI Rematch

To test AI code generation capabilities, an isolated AI version was generated in quarantine under `ai-version/` and compared against our hand-built decoupled Clean Architecture implementation.

### 📝 Full Initial Prompt Used
```text
Build a Python FastAPI REST API backed by SQLite using Python's standard library `sqlite3` stored in `tasks.db`.
1. Database Setup: On startup, open tasks.db. Create table 'tasks' if missing with columns: id (INTEGER PRIMARY KEY AUTOINCREMENT), title (TEXT NOT NULL), done (INTEGER NOT NULL DEFAULT 0).
2. Seeding: Count rows in tasks table. If count is 0, insert 3 example tasks: ("Buy groceries", 0), ("Read a book", 0), ("Learn SQLite", 1). Do not re-seed on restart if rows exist.
3. CRUD Endpoints:
   - GET /tasks -> SELECT * FROM tasks (return list of Task)
   - GET /tasks/{id} -> SELECT * FROM tasks WHERE id = ? (404 with {"error": "Task not found"} if missing)
   - POST /tasks -> INSERT INTO tasks (title, done) VALUES (?, 0) (400 with {"error": "Title is required"} if title is empty/missing; return 201 Created)
   - PUT /tasks/{id} -> UPDATE tasks SET title = ?, done = ? WHERE id = ? (400 if title empty or done missing, 404 if id missing; return 200 OK)
   - DELETE /tasks/{id} -> DELETE FROM tasks WHERE id = ? (404 if id missing; 204 No Content on success)
4. Use parameterized queries with ? for all SQL commands.
```

### 🔬 Analysis & Concrete Differences

1. **What Did the AI Do Better?**
   - **Bulk Insertion with `executemany`**: The AI used `cursor.executemany()` with a list of tuples `[("Buy groceries", 0), ("Read a book", 0), ("Learn SQLite", 1)]` for the initial seed data. This is more concise and idiomatic for multi-row insertion in `sqlite3`.

2. **What Did It Get Wrong or Quietly Ignore?**
   - **Relative Path Resolution Issue**: The AI hardcoded `DB_PATH = Path("tasks.db")`. When running the application from a different working directory, SQLite created `tasks.db` in that local directory rather than resolving relative to the package root.
   - **Inline DB Connections & Connection Leak Risk**: Instead of using a dedicated Repository pattern or context manager, the AI opened and closed DB connections inline inside every route handler (`conn = get_db()` ... `conn.close()`). If an exception occurred prior to `conn.close()`, connection handles were left open.
   - **Validation Error Status Codes**: Strict Pydantic type validation in the AI's models caused missing request fields to trigger FastAPI's default `422 Unprocessable Entity` response instead of returning the required `400 Bad Request` with `{"error": "Title is required"}`.

3. **What Did the Prompt Forget to Specify & What Did the AI Silently Decide?**
   - **Architecture & Layer Decoupling**: The prompt did not specify architecture design patterns. The AI silently decided to create a single monolithic script with inline database operations inside API routes instead of creating domain entities and repository classes.

### 🔄 Rematch & Prompt Iteration
In the second rematch iteration, explicitly specifying the Repository Pattern and `Path(__file__).parent` path resolution resulted in clean, leak-free connection management and correct HTTP 400 validation error responses.
