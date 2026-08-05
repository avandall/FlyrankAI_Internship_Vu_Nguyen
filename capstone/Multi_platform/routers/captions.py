from fastapi import APIRouter, HTTPException
from capstone.Multi_platform.services.captions import CaptionGenerator
from capstone.Multi_platform.core.config import PLATFORM_SPECS

router = APIRouter(prefix="/api/captions", tags=["Captions Preview"])
caption_gen = CaptionGenerator()

@router.post("/preview", summary="Preview platform-tailored captions")
def preview_captions(body: dict):
    title = body.get("title", "")
    content = body.get("content", "")
    if not title or not content:
        raise HTTPException(status_code=422, detail="title and content required")

    captions = {}
    for platform in PLATFORM_SPECS:
        cap = caption_gen.generate(platform, content, title)
        captions[platform] = {
            "caption": cap,
            "length": len(cap),
            "max_allowed": PLATFORM_SPECS[platform]["max_caption_chars"],
            "within_limit": len(cap) <= PLATFORM_SPECS[platform]["max_caption_chars"],
            "platform_style": PLATFORM_SPECS[platform]["style"],
        }
    return {"captions": captions}
