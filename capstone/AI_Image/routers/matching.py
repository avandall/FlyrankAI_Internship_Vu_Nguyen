from fastapi import APIRouter, HTTPException

from capstone.AI_Image.services.matching import ContentMatchingEngine

router = APIRouter(prefix="/api/match", tags=["Matching"])
matching_engine = ContentMatchingEngine()

@router.post("", summary="Match blog post to best image")
def match_post(body: dict):
    post_id = body.get("post_id", f"p_{id(body)}")
    title = body.get("title", "")
    text = body.get("text", "")
    if not (title or text):
        raise HTTPException(status_code=422, detail="Provide at least 'title' or 'text'")
    
    result = matching_engine.match_post(
        post_id=post_id,
        title=title,
        text=text,
        target_subject=body.get("target_subject"),
        target_category=body.get("target_category"),
    )
    return result
