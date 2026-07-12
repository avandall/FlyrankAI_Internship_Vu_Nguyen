from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import router as jobs_router
from app.core.database import db
from app.core.redis_client import redis_client
from app.repositories.postgres import PostgresJobRepository
from app.services.job_service import JobService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the database connection pool and Redis client
    await db.connect()
    redis_client.connect()
    
    # Instantiate the Postgres-backed repository and inject it into the service
    job_repository = PostgresJobRepository(pool=db.pool)
    job_service = JobService(repository=job_repository)
    
    # Save the service to app state so routes can consume it
    app.state.job_service = job_service
    
    yield
    
    # Shutdown: Close database and Redis pool connections
    await db.disconnect()
    await redis_client.disconnect()

app = FastAPI(title="FlyrankAI API", lifespan=lifespan)

# Include routes
app.include_router(jobs_router)

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