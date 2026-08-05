import os
import uuid
import json
import hashlib
import logging
from typing import Dict, Optional, List
from datetime import datetime
from pathlib import Path

from capstone.Multi_platform.core.database import get_db_pool
from capstone.Multi_platform.services.variants import ImageVariantPipeline
from capstone.Multi_platform.services.captions import CaptionGenerator

logger = logging.getLogger(__name__)

class CampaignService:
    def __init__(self):
        self.image_pipeline = ImageVariantPipeline()
        self.caption_gen = CaptionGenerator()

    async def create_campaign(self, title: str, content: str,
                        platforms: List[str], image_bytes: Optional[bytes] = None) -> Dict:
        campaign_id = f"camp_{uuid.uuid4().hex[:10]}"
        image_path = None

        if image_bytes:
            img_dir = Path(__file__).parent.parent / "static" / "image_variants"
            img_dir.mkdir(parents=True, exist_ok=True)
            image_path = str(img_dir / f"{campaign_id}_original.jpg")
            with open(image_path, "wb") as f:
                f.write(image_bytes)

        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO campaigns (campaign_id, title, content, platforms, status, image_path, created_at, updated_at)
                VALUES ($1,$2,$3,$4,$5,$6, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, campaign_id, title, content, json.dumps(platforms), "draft", image_path)

        return {"campaign_id": campaign_id, "title": title, "status": "draft",
                "platforms": platforms, "image_path": image_path}

    async def publish_campaign(self, campaign_id: str) -> Dict:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM campaigns WHERE campaign_id=$1", campaign_id)

        if not row:
            raise ValueError(f"Campaign not found: {campaign_id}")

        campaign = dict(row)
        platforms = json.loads(campaign["platforms"])
        results = {}

        image_bytes = None
        if campaign.get("image_path") and os.path.exists(campaign["image_path"]):
            with open(campaign["image_path"], "rb") as f:
                image_bytes = f.read()

        variants = {}
        if image_bytes:
            try:
                # Pillow manipulation is synchronous, but fast enough for this scale
                variants = self.image_pipeline.create_variants(image_bytes, campaign_id)
            except Exception as e:
                logger.warning(f"Image variant creation failed: {e}")

        async with pool.acquire() as conn:
            for platform in platforms:
                caption = self.caption_gen.generate(
                    platform, campaign["content"], campaign["title"]
                )

                idem_key = hashlib.sha256(
                    f"{campaign_id}:{platform}".encode()
                ).hexdigest()[:32]

                existing = await conn.fetchrow(
                    "SELECT * FROM platform_posts WHERE idempotency_key=$1", idem_key
                )

                if existing:
                    results[platform] = {"status": "already_published (idempotent)", "post_id": existing["post_id"]}
                    continue

                post_id = f"post_{uuid.uuid4().hex[:8]}"
                variant_path = variants.get(platform, {}).get("path")
                variant_w = variants.get(platform, {}).get("width")
                variant_h = variants.get(platform, {}).get("height")

                await conn.execute("""
                    INSERT INTO platform_posts
                    (post_id, campaign_id, platform, idempotency_key, status, caption,
                     image_variant_path, image_width, image_height, created_at)
                    VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9, CURRENT_TIMESTAMP)
                """, post_id, campaign_id, platform, idem_key, "queued", caption,
                      variant_path, variant_w, variant_h)
                
                results[platform] = {
                    "post_id": post_id, "status": "queued",
                    "caption_preview": caption[:100] + "...",
                    "image_size": f"{variant_w}x{variant_h}" if variant_w else "no image",
                }

            await conn.execute(
                "UPDATE campaigns SET status=$1, updated_at=$2 WHERE campaign_id=$3",
                "publishing", datetime.utcnow().isoformat(), campaign_id
            )

        # Enqueue task for background worker
        from capstone.Multi_platform.worker import redis_client
        await redis_client.lpush("campaign_queue", json.dumps({"campaign_id": campaign_id}))

        return {"campaign_id": campaign_id, "results": results}

    async def get_campaign(self, campaign_id: str) -> Optional[Dict]:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM campaigns WHERE campaign_id=$1", campaign_id)
            if not row:
                return None
            posts = await conn.fetch("SELECT * FROM platform_posts WHERE campaign_id=$1", campaign_id)
            
        camp = dict(row)
        camp["platforms"] = json.loads(camp["platforms"])
        camp["posts"] = [dict(p) for p in posts]
        return camp

    async def get_all_campaigns(self) -> List[Dict]:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM campaigns ORDER BY created_at DESC LIMIT 20")
        return [dict(r) for r in rows]
