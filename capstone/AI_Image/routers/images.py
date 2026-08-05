from fastapi import APIRouter, HTTPException

from capstone.AI_Image.services.ingestion import ImageIngestionService

router = APIRouter(prefix="/api/images", tags=["Image Library"])
ingestion_svc = ImageIngestionService()

@router.get("", summary="List all ingested images")
def get_images():
    return {"images": ingestion_svc.get_all_images()}

@router.get("/{image_id}", summary="Get single image metadata")
def get_image(image_id: str):
    img = ingestion_svc.get_image(image_id)
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    return img
