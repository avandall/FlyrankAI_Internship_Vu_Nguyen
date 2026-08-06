from typing import Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from capstone.AI_Image.services.ingestion import ImageIngestionService

router = APIRouter(prefix="/api/ingest", tags=["Image Ingestion"])
ingestion_svc = ImageIngestionService()

@router.post("/upload", summary="Upload single image file for AI analysis")
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
        result = await ingestion_svc.ingest_from_file(file.filename or "upload.jpg", file_bytes, image_id)
        return {"status": "success", "image": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-batch", summary="Upload multiple image files in batch for AI analysis")
async def upload_batch_images(
    files: List[UploadFile] = File(..., description="List of image files (jpg/png/webp)"),
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided for batch upload.")
    
    allowed_types = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
    results = []
    queued_count = 0
    duplicate_count = 0

    for file in files:
        filename = file.filename or "upload.jpg"
        if file.content_type not in allowed_types:
            results.append({
                "filename": filename,
                "status": "error",
                "message": f"Unsupported content type: {file.content_type}"
            })
            continue

        file_bytes = await file.read()
        if len(file_bytes) > 10 * 1024 * 1024:
            results.append({
                "filename": filename,
                "status": "error",
                "message": "File exceeds 10MB limit"
            })
            continue

        try:
            res = await ingestion_svc.ingest_from_file(filename, file_bytes)
            if res.get("is_duplicate"):
                duplicate_count += 1
            else:
                queued_count += 1
            results.append(res)
        except Exception as e:
            results.append({
                "filename": filename,
                "status": "error",
                "message": str(e)
            })

    return {
        "status": "success",
        "total_files": len(files),
        "queued_count": queued_count,
        "duplicate_count": duplicate_count,
        "results": results
    }

@router.post("/metadata", summary="Ingest image by metadata (seeding)")
async def ingest_metadata(body: dict):
    required = ["image_id", "filename", "subject", "category", "caption", "confidence_score"]
    for field in required:
        if field not in body:
            raise HTTPException(status_code=422, detail=f"Missing required field: {field}")
    result = await ingestion_svc.ingest_metadata(body)
    return {"status": "success", "image": result}
