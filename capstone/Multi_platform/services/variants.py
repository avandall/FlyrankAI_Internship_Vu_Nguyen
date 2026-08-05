import io
from pathlib import Path
from typing import Dict
from PIL import Image

from capstone.Multi_platform.core.config import PLATFORM_SPECS

class ImageVariantPipeline:
    """
    Takes 1 source image, produces platform-specific variants.
    Ensures subject stays in safe zone by center-cropping rather than
    stretching (maintains aspect ratio integrity).
    """

    OUTPUT_DIR = Path(__file__).parent.parent / "static" / "image_variants"

    def __init__(self):
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def create_variants(self, source_bytes: bytes, campaign_id: str) -> Dict[str, Dict]:
        source_img = Image.open(io.BytesIO(source_bytes))
        if source_img.mode not in ("RGB", "RGBA"):
            source_img = source_img.convert("RGB")

        variants = {}
        for platform, spec in PLATFORM_SPECS.items():
            variant_path = self._create_variant(source_img, campaign_id, platform, spec)
            variants[platform] = {
                "path": str(variant_path),
                "width": spec["width"],
                "height": spec["height"],
                "ratio": spec["ratio"],
            }
        return variants

    def _create_variant(
        self, img: Image.Image, campaign_id: str,
        platform: str, spec: Dict,
    ) -> Path:
        target_w, target_h = spec["width"], spec["height"]
        target_ratio = target_w / target_h
        src_w, src_h = img.size
        src_ratio = src_w / src_h

        if src_ratio > target_ratio:
            scale_h = target_h
            scale_w = int(src_w * target_h / src_h)
        else:
            scale_w = target_w
            scale_h = int(src_h * target_w / src_w)

        resized = img.resize((scale_w, scale_h), Image.LANCZOS)
        left = (scale_w - target_w) // 2
        top = (scale_h - target_h) // 2
        right = left + target_w
        bottom = top + target_h
        cropped = resized.crop((left, top, right, bottom))

        filename = f"{campaign_id}_{platform}_{target_w}x{target_h}.jpg"
        out_path = self.OUTPUT_DIR / filename
        cropped.save(str(out_path), "JPEG", quality=92)
        return out_path
