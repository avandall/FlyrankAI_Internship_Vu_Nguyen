from fastapi import APIRouter, HTTPException

from capstone.AI_Image.services.ingestion import ImageIngestionService

router = APIRouter(prefix="/api", tags=["Jobs and Costs"])
ingestion_svc = ImageIngestionService()

@router.get("/jobs/{job_id}", summary="Get job status (background processing)")
async def get_job(job_id: str):
    job = await ingestion_svc.get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/costs", summary="AI cost summary per ingest job")
async def get_cost_summary():
    return await ingestion_svc.get_cost_summary()
