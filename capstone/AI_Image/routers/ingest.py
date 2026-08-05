from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from capstone.AI_Image.services.ingestion import ImageIngestionService

router = APIRouter(prefix="/api/ingest", tags=["Image Ingestion"])
ingestion_svc = ImageIngestionService()

@router.post("/upload", summary="Upload image file for AI analysis")
async def upload_image(
    file: UploadFile = File(..., description="Image file (jpg/png/webp)"),
    image_id: Optional[str] = Form(None),
):
    allowed_types = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}. Use jpg/png/webp.")
    
    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=413, detail="File too large. Maximum 10MB.")
    
    try:
        result = ingestion_svc.ingest_from_file(file.filename or "upload.jpg", file_bytes, image_id)
        return {"status": "success", "image": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/metadata", summary="Ingest image by metadata (seeding)")
def ingest_metadata(body: dict):
    required = ["image_id", "filename", "subject", "category", "caption", "confidence_score"]
    for field in required:
        if field not in body:
            raise HTTPException(status_code=422, detail=f"Missing required field: {field}")
    result = ingestion_svc.ingest_metadata(body)
    return {"status": "success", "image": result}
