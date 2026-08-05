from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from capstone.AI_Image.services.matching import ContentMatchingEngine

router = APIRouter(tags=["Matching"])
matching_engine = ContentMatchingEngine()

@router.get("/posts/{post_id}/images", summary="Match blog post to best image")
async def match_post(
    post_id: str,
    title: str = Query(""),
    text: str = Query(""),
    target_subject: Optional[str] = Query(None),
    target_category: Optional[str] = Query(None),
):
    if not (title or text):
        # In a real app we might fetch the post from DB here using post_id
        # For demo purposes without a full blog backend, we accept them as query params
        raise HTTPException(status_code=422, detail="Provide at least 'title' or 'text' query parameters")
    
    result = await matching_engine.match_post(
        post_id=post_id,
        title=title,
        text=text,
        target_subject=target_subject,
        target_category=target_category,
    )
    return result
