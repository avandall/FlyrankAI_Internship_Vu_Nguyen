from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import router as jobs_router
from app.api.task_routes import router as tasks_router
from app.core.database import db
from app.core.redis_client import redis_client
from app.core.sqlite_db import init_sqlite_db
from app.repositories.postgres import PostgresJobRepository
from app.services.job_service import JobService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize SQLite tasks DB
    init_sqlite_db()

    # Startup: Initialize the database connection pool and Redis client
    try:
        await db.connect()
    except Exception as e:
        print(f"Postgres connection warning: {e}")

    try:
        redis_client.connect()
    except Exception as e:
        print(f"Redis connection warning: {e}")
    
    # Instantiate the Postgres-backed repository and inject it into the service
    if db.pool:
        job_repository = PostgresJobRepository(pool=db.pool)
        job_service = JobService(repository=job_repository)
        app.state.job_service = job_service
    
    yield
    
    # Shutdown: Close database and Redis pool connections
    try:
        await db.disconnect()
        await redis_client.disconnect()
    except Exception:
        pass

app = FastAPI(title="FlyrankAI API", lifespan=lifespan)

# Include routes
app.include_router(jobs_router)
app.include_router(tasks_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to my FlyrankAI!"}

@app.get("/status")
async def get_status():
    redis_alive = await redis_client.ping()
    return {
        "status": "healthy",
        "version": "1.0.0",
        "redis_connected": redis_alive
    }