from fastapi import APIRouter
from capstone.Multi_platform.core.config import PLATFORM_SPECS

router = APIRouter(prefix="/api/platforms", tags=["Platforms"])

@router.get("", summary="Platform specs (image dimensions, caption limits)")
def get_platforms():
    return {"platforms": PLATFORM_SPECS}
