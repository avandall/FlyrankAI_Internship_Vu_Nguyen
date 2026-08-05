import os
import uuid
import json
import hashlib
import logging
from typing import Dict, Optional, List
from datetime import datetime
from pathlib import Path

from capstone.Multi_platform.core.database import get_db
from capstone.Multi_platform.services.variants import ImageVariantPipeline
from capstone.Multi_platform.services.captions import CaptionGenerator
from capstone.Multi_platform.services.publishers import PublisherAdapterFactory

logger = logging.getLogger(__name__)

class CampaignService:
    def __init__(self):
        self.image_pipeline = ImageVariantPipeline()
        self.caption_gen = CaptionGenerator()

    def create_campaign(self, title: str, content: str,
                        platforms: List[str], image_bytes: Optional[bytes] = None) -> Dict:
        campaign_id = f"camp_{uuid.uuid4().hex[:10]}"
        image_path = None

        if image_bytes:
            img_dir = Path(__file__).parent.parent / "static" / "image_variants"
            img_dir.mkdir(parents=True, exist_ok=True)
            image_path = str(img_dir / f"{campaign_id}_original.jpg")
            with open(image_path, "wb") as f:
                f.write(image_bytes)

        with get_db() as conn:
            conn.execute("""
                INSERT INTO campaigns (campaign_id, title, content, platforms, status, image_path)
                VALUES (?,?,?,?,?,?)
            """, (campaign_id, title, content, json.dumps(platforms), "draft", image_path))
            conn.commit()

        return {"campaign_id": campaign_id, "title": title, "status": "draft",
                "platforms": platforms, "image_path": image_path}

    def publish_campaign(self, campaign_id: str) -> Dict:
        with get_db() as conn:
            row = conn.execute(
                "SELECT * FROM campaigns WHERE campaign_id=?", (campaign_id,)
            ).fetchone()

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
                variants = self.image_pipeline.create_variants(image_bytes, campaign_id)
            except Exception as e:
                logger.warning(f"Image variant creation failed: {e}")

        for platform in platforms:
            caption = self.caption_gen.generate(
                platform, campaign["content"], campaign["title"]
            )

            idem_key = hashlib.sha256(
                f"{campaign_id}:{platform}".encode()
            ).hexdigest()[:32]

            with get_db() as conn:
                existing = conn.execute(
                    "SELECT * FROM platform_posts WHERE idempotency_key=?", (idem_key,)
                ).fetchone()

            if existing:
                results[platform] = {"status": "already_published (idempotent)", "post_id": existing["post_id"]}
                continue

            post_id = f"post_{uuid.uuid4().hex[:8]}"
            variant_path = variants.get(platform, {}).get("path")
            variant_w = variants.get(platform, {}).get("width")
            variant_h = variants.get(platform, {}).get("height")

            with get_db() as conn:
                conn.execute("""
                    INSERT INTO platform_posts
                    (post_id, campaign_id, platform, idempotency_key, status, caption,
                     image_variant_path, image_width, image_height)
                    VALUES (?,?,?,?,?,?,?,?,?)
                """, (post_id, campaign_id, platform, idem_key, "queued", caption,
                      variant_path, variant_w, variant_h))
                conn.commit()

            try:
                adapter = PublisherAdapterFactory.get(platform)
                success, message, ext_post_id = adapter.publish(
                    caption, variant_path, idem_key
                )
                status = "published" if success else "failed"
                with get_db() as conn:
                    conn.execute("""
                        UPDATE platform_posts
                        SET status=?, external_post_id=?, publish_attempts=1,
                            published_at=?, last_error=?
                        WHERE post_id=?
                    """, (status, ext_post_id, datetime.utcnow().isoformat() if success else None,
                          None if success else message, post_id))
                    conn.commit()
                results[platform] = {
                    "post_id": post_id, "status": status,
                    "external_post_id": ext_post_id, "message": message,
                    "caption_preview": caption[:100] + "...",
                    "image_size": f"{variant_w}x{variant_h}" if variant_w else "no image",
                }
            except Exception as e:
                results[platform] = {"post_id": post_id, "status": "failed", "error": str(e)}

        all_published = all(r.get("status") in ("published", "already_published (idempotent)")
                           for r in results.values())
        with get_db() as conn:
            conn.execute(
                "UPDATE campaigns SET status=?, updated_at=? WHERE campaign_id=?",
                ("published" if all_published else "partial", datetime.utcnow().isoformat(), campaign_id)
            )
            conn.commit()

        return {"campaign_id": campaign_id, "results": results}

    def get_campaign(self, campaign_id: str) -> Optional[Dict]:
        with get_db() as conn:
            row = conn.execute("SELECT * FROM campaigns WHERE campaign_id=?", (campaign_id,)).fetchone()
            if not row:
                return None
            posts = conn.execute(
                "SELECT * FROM platform_posts WHERE campaign_id=?", (campaign_id,)
            ).fetchall()
        camp = dict(row)
        camp["platforms"] = json.loads(camp["platforms"])
        camp["posts"] = [dict(p) for p in posts]
        return camp

    def get_all_campaigns(self) -> List[Dict]:
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM campaigns ORDER BY created_at DESC LIMIT 20").fetchall()
        return [dict(r) for r in rows]
