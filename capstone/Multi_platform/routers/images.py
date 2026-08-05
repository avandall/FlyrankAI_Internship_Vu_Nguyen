from fastapi import APIRouter, UploadFile, File
from capstone.Multi_platform.services.variants import ImageVariantPipeline

router = APIRouter(prefix="/api/image", tags=["Image Variants Preview"])
image_pipeline = ImageVariantPipeline()

@router.post("/variants", summary="Generate image variants from upload")
async def preview_image_variants(image: UploadFile = File(...)):
    img_bytes = await image.read()
    variants = image_pipeline.create_variants(img_bytes, "preview")
    return {
        "source_filename": image.filename,
        "variants": {
            platform: {
                "width": v["width"],
                "height": v["height"],
                "ratio": v["ratio"],
                "filename": v["path"].split("/")[-1] if v.get("path") else None,
            }
            for platform, v in variants.items()
        }
    }
