import json
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from capstone.Multi_platform.services.campaign import CampaignService
from capstone.Multi_platform.core.config import PLATFORM_SPECS

router = APIRouter(prefix="/api/campaigns", tags=["Campaigns"])
campaign_svc = CampaignService()

@router.get("", summary="List all campaigns")
async def list_campaigns():
    return {"campaigns": await campaign_svc.get_all_campaigns()}

@router.get("/{campaign_id}", summary="Get campaign with post statuses")
async def get_campaign(campaign_id: str):
    campaign = await campaign_svc.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@router.post("", status_code=201, summary="Create new campaign")
async def create_campaign(
    title: str = Form(...),
    content: str = Form(...),
    platforms: str = Form(..., description="JSON array: ['instagram','twitter']"),
    image: Optional[UploadFile] = File(None),
):
    try:
        platform_list = json.loads(platforms)
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="platforms must be valid JSON array")

    valid_platforms = set(PLATFORM_SPECS.keys())
    invalid = [p for p in platform_list if p not in valid_platforms]
    if invalid:
        raise HTTPException(status_code=422, detail=f"Unknown platforms: {invalid}. Valid: {list(valid_platforms)}")

    image_bytes = None
    if image:
        image_bytes = await image.read()

    result = await campaign_svc.create_campaign(title, content, platform_list, image_bytes)
    return {"status": "created", "campaign": result}

@router.post("/{campaign_id}/publish", summary="Publish campaign to all platforms")
async def publish_campaign(campaign_id: str):
    try:
        result = await campaign_svc.publish_campaign(campaign_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
