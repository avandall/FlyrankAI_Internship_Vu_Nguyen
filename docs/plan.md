# Implementation Plan: Postgres & Clean Architecture

## 1. Clean Architecture Structure
We will organize the code using a decoupled, clean architecture skeleton:
```
flyrankai/
├── app/
│   ├── domain/           # Entities (models) & Repository Interfaces
│   │   ├── entities.py   # Job entity definition
│   │   └── interfaces.py # JobRepository interface
│   ├── repositories/     # Storage implementations
│   │   ├── in_memory.py  # InMemoryJobRepository
│   │   └── postgres.py   # PostgresJobRepository
│   ├── services/         # Business logic / Use Cases
│   │   └── job_service.py
│   ├── api/              # FastAPI routes
│   │   └── routes.py
│   └── core/             # Configuration & DB connection pool
│       ├── config.py
│       └── database.py
├── docs/
│   ├── guiding.md
│   └── plan.md
├── main.py               # App entrypoint (initializes routes & dependencies)
├── docker-compose.yml    # App & Database containers
├── init.sql              # Database schema initialization script
├── .env.example          # Template for environment variables
└── .env                  # Environment variables (gitignored)
```

---

## 2. Step-by-Step Execution Plan

### Step 1: Clean Architecture Skeleton & In-Memory Store
1. **Domain & Interface**: 
   - Define a `Job` domain entity (ID, Title, Company, Description, Created At).
   - Define an abstract `JobRepository` interface with `create`, `get_by_id`, and `list_all` methods.
2. **In-Memory Storage**:
   - Implement `InMemoryJobRepository` using a Python dictionary.
3. **Business Logic & API**:
   - Implement `JobService` that interacts with the `JobRepository`.
   - Set up API routes in `app/api/routes.py` (`POST /jobs`, `GET /jobs`, `GET /jobs/{id}`) interacting ONLY with `JobService`.
   - Update `main.py` to wire everything together using dependency injection.

### Step 2: Postgres & Docker Setup
1. **Docker Compose**:
   - Define `docker-compose.yml` to spin up:
     - A Postgres database container with a persistent Docker volume (`pgdata`).
     - The FastAPI app container (built from a local `Dockerfile`).
2. **Environment Configuration**:
   - Create `.env.example` containing `DATABASE_URL`.
   - Create `.env` (gitignored) with the local Postgres connection details.
3. **Database Schema**:
   - Create `init.sql` to initialize the `jobs` table in Postgres.

### Step 3: Postgres Repository Implementation & Swap
1. **Dependencies**:
   - Install a database client (e.g., `asyncpg` or `psycopg` via `uv add`).
2. **Database Connector**:
   - Set up db connection pooling in `app/core/database.py`.
3. **Postgres Repo**:
   - Implement `PostgresJobRepository` conforming to the `JobRepository` interface.
4. **Swap Storage**:
   - In `main.py`, replace `InMemoryJobRepository` with `PostgresJobRepository`.
   - Verify that no api routes or service layer logic changes.

### Step 4: Verification & Persistence Proof
1. Run `docker compose up --build` to start the app and database.
2. Insert a job using `POST /jobs`.
3. Verify it is saved using `GET /jobs`.
4. Run `docker compose restart` (or stop and restart the containers).
5. Run `GET /jobs` again to confirm that data persists.
