from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.domain.entities import Job
from app.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["Jobs"])

# Dependency to get the JobService from FastAPI app state
def get_job_service(request: Request) -> JobService:
    return request.app.state.job_service

@router.post("/", response_model=Job, status_code=status.HTTP_201_CREATED)
async def create_job(job: Job, service: JobService = Depends(get_job_service)):
    # Check if job with the same ID already exists
    if await service.get_job(job.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job with ID '{job.id}' already exists."
        )
    return await service.create_job(job)

@router.get("/", response_model=list[Job])
async def list_jobs(service: JobService = Depends(get_job_service)):
    return await service.list_jobs()

@router.get("/{job_id}", response_model=Job)
async def get_job(job_id: str, service: JobService = Depends(get_job_service)):
    job = await service.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{job_id}' not found."
        )
    return job
