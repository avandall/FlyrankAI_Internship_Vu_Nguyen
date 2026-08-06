import uuid
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import base64

from capstone.AI_Image.core.database import get_db_pool
from capstone.AI_Image.worker import redis_client, QUEUE_NAME

logger = logging.getLogger(__name__)

class ImageIngestionService:
    """Handles file upload → Queues job to Redis."""

    async def ingest_from_file(
        self,
        filename: str,
        file_bytes: bytes,
        image_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        1. Calculate SHA-256 hash to validate deduplication
        2. If duplicate exists in DB, return existing record
        3. Otherwise save file & queue job to Redis
        """
        from capstone.AI_Image.utils import compute_image_hashes
        file_hash, perceptual_hash = compute_image_hashes(file_bytes)

        pool = await get_db_pool()
        async with pool.acquire() as conn:
            existing_img = await conn.fetchrow(
                "SELECT image_id, filename FROM images WHERE file_hash=$1 OR perceptual_hash=$2 OR filename=$3",
                file_hash, perceptual_hash, filename
            )
            if existing_img:
                logger.info(f"Duplicate image detected in DB: {filename} (hash: {file_hash[:10]}...). Deduplicated.")
                return {
                    "image_id": existing_img["image_id"],
                    "filename": existing_img["filename"],
                    "status": "duplicate",
                    "is_duplicate": True,
                    "message": f"Duplicate image content detected! Image already exists in DB ({existing_img['image_id']} — {existing_img['filename']}). Upload rejected to prevent duplicates."
                }

            existing_job = await conn.fetchrow(
                "SELECT image_id FROM ingest_jobs WHERE file_hash=$1 OR perceptual_hash=$2",
                file_hash, perceptual_hash
            )
            if existing_job:
                logger.info(f"Duplicate image detected in queued jobs: {filename} (hash: {file_hash[:10]}...). Deduplicated.")
                return {
                    "image_id": existing_job["image_id"],
                    "filename": filename,
                    "status": "duplicate",
                    "is_duplicate": True,
                    "message": f"Duplicate image content is already queued for processing ({existing_job['image_id']}). Upload rejected to prevent duplicates."
                }

        image_id = image_id or f"img_{uuid.uuid4().hex[:10]}"
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        
        # Save real uploaded image file bytes directly to static/uploads/
        uploads_dir = Path(__file__).parent.parent / "static" / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        (uploads_dir / filename).write_bytes(file_bytes)
        (uploads_dir / f"{image_id}_{filename}").write_bytes(file_bytes)

        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO ingest_jobs (job_id, image_id, status, file_hash, perceptual_hash) VALUES ($1, $2, 'queued', $3, $4)",
                job_id, image_id, file_hash, perceptual_hash
            )

        file_bytes_b64 = base64.b64encode(file_bytes).decode('utf-8')
        
        # Push to Redis
        await redis_client.rpush(QUEUE_NAME, json.dumps({
            "job_id": job_id,
            "image_id": image_id,
            "filename": filename,
            "file_bytes_b64": file_bytes_b64,
            "file_hash": file_hash
        }))

        return {
            "image_id": image_id,
            "job_id": job_id,
            "filename": filename,
            "status": "queued",
            "is_duplicate": False,
            "message": "Image queued for asynchronous Vision AI processing"
        }

    async def ingest_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Direct metadata ingest (for seeding without file upload)."""
        import hashlib
        from capstone.AI_Image.utils import compute_embedding
        from capstone.AI_Image.core.config import CONFIDENCE_THRESHOLD
        
        embed_text = f"{metadata['caption']} {metadata['subject']} {' '.join(metadata.get('attributes', []))}"
        embedding = await compute_embedding(embed_text)
        is_flagged = metadata.get("confidence_score", 1.0) < CONFIDENCE_THRESHOLD
        file_hash = metadata.get("file_hash") or hashlib.sha256(metadata["filename"].encode()).hexdigest()

        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO images (
                    image_id, filename, file_size_bytes, format, width, height,
                    subject, category, attributes, caption, confidence_score, is_flagged, embedding, file_hash
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                ON CONFLICT (image_id) DO UPDATE SET
                    subject=EXCLUDED.subject,
                    category=EXCLUDED.category,
                    attributes=EXCLUDED.attributes,
                    caption=EXCLUDED.caption,
                    confidence_score=EXCLUDED.confidence_score,
                    is_flagged=EXCLUDED.is_flagged,
                    embedding=EXCLUDED.embedding,
                    file_hash=EXCLUDED.file_hash
            """,
                metadata["image_id"], metadata["filename"],
                metadata.get("file_size_bytes", 0), metadata.get("format", "jpg"),
                metadata.get("width"), metadata.get("height"),
                metadata["subject"], metadata["category"],
                json.dumps(metadata.get("attributes", [])),
                metadata["caption"], metadata.get("confidence_score", 0.9),
                1 if is_flagged else 0,
                json.dumps(embedding),
                file_hash,
            )
        
        return {**metadata, "is_flagged": is_flagged, "embedding_dim": len(embedding)}

    def _attach_image_url(self, d: Dict[str, Any]) -> Dict[str, Any]:
        image_id = d.get("image_id", "")
        d["image_url"] = f"/api/images/{image_id}/file"
        return d

    async def get_image(self, image_id: str) -> Optional[Dict]:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM images WHERE image_id=$1", image_id)
        if not row:
            return None
        d = dict(row)
        if d.get("attributes") and isinstance(d["attributes"], str):
            d["attributes"] = json.loads(d["attributes"])
        d.pop("embedding", None)
        return self._attach_image_url(d)

    async def get_all_images(self) -> List[Dict]:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM images ORDER BY created_at DESC")
        
        result = []
        for row in rows:
            d = dict(row)
            if d.get("attributes") and isinstance(d["attributes"], str):
                d["attributes"] = json.loads(d["attributes"])
            d.pop("embedding", None)
            result.append(self._attach_image_url(d))
        return result

    async def get_job_status(self, job_id: str) -> Optional[Dict]:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM ingest_jobs WHERE job_id=$1", job_id)
        return dict(row) if row else None

    async def get_cost_summary(self) -> Dict[str, Any]:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT status, COUNT(*) as count, SUM(ai_cost_micro_usd) as total_cost
                FROM ingest_jobs GROUP BY status
            """)
        summary = {row["status"]: {"count": row["count"], "cost_micro_usd": row["total_cost"] or 0} for row in rows}
        total = sum(v["cost_micro_usd"] for v in summary.values())
        return {"by_status": summary, "total_cost_micro_usd": total, "total_cost_usd": f"${total/1_000_000:.6f}"}
