from typing import Optional
from fastapi import APIRouter, Query

from capstone.AI_Image.services.review import ReviewService

router = APIRouter(tags=["Reviews"])
review_svc = ReviewService()

@router.post("/images/review", summary="Submit human review (approve/reject suggestion)")
async def submit_review(body: dict):
    result = await review_svc.submit_review(
        image_id=body.get("image_id", ""),
        post_id=body.get("post_id", ""),
        approved=body.get("approved", False),
        reject_reason=body.get("reject_reason"),
        reviewer=body.get("reviewer", "human_editor"),
    )
    return result

@router.get("/images/reviews", summary="Get all reviews or filter by image")
async def get_reviews(image_id: Optional[str] = Query(None)):
    return {"reviews": await review_svc.get_reviews(image_id)}

@router.get("/metrics/precision", summary="Top-1 Precision metric report")
async def get_precision():
    return await review_svc.get_top1_precision()
