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
        1. Create batch job record in Postgres
        2. Push job to Redis queue
        """
        image_id = image_id or f"img_{uuid.uuid4().hex[:10]}"
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO ingest_jobs (job_id, image_id, status) VALUES ($1, $2, 'queued')",
                job_id, image_id
            )

        file_bytes_b64 = base64.b64encode(file_bytes).decode('utf-8')
        
        # Push to Redis
        await redis_client.rpush(QUEUE_NAME, json.dumps({
            "job_id": job_id,
            "image_id": image_id,
            "filename": filename,
            "file_bytes_b64": file_bytes_b64
        }))

        return {
            "image_id": image_id,
            "job_id": job_id,
            "filename": filename,
            "status": "queued",
            "message": "Image queued for asynchronous processing"
        }

    async def ingest_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Direct metadata ingest (for seeding without file upload).
        For simplicity, seed data skips Groq/Ollama and uses mock embeddings so we don't spam APIs on startup.
        """
        from capstone.AI_Image.utils import compute_embedding
        from capstone.AI_Image.core.config import CONFIDENCE_THRESHOLD
        
        # Seed script might run synchronously initially, so we just use mock or async call.
        embed_text = f"{metadata['caption']} {metadata['subject']} {' '.join(metadata.get('attributes', []))}"
        embedding = await compute_embedding(embed_text)
        is_flagged = metadata.get("confidence_score", 1.0) < CONFIDENCE_THRESHOLD
        
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO images (
                    image_id, filename, file_size_bytes, format, width, height,
                    subject, category, attributes, caption, confidence_score, is_flagged, embedding
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                ON CONFLICT (image_id) DO UPDATE SET
                    subject=EXCLUDED.subject,
                    category=EXCLUDED.category,
                    attributes=EXCLUDED.attributes,
                    caption=EXCLUDED.caption,
                    confidence_score=EXCLUDED.confidence_score,
                    is_flagged=EXCLUDED.is_flagged,
                    embedding=EXCLUDED.embedding
            """,
                metadata["image_id"], metadata["filename"],
                metadata.get("file_size_bytes", 0), metadata.get("format", "jpg"),
                metadata.get("width"), metadata.get("height"),
                metadata["subject"], metadata["category"],
                json.dumps(metadata.get("attributes", [])),
                metadata["caption"], metadata.get("confidence_score", 0.9),
                1 if is_flagged else 0,
                json.dumps(embedding),
            )
        
        return {**metadata, "is_flagged": is_flagged, "embedding_dim": len(embedding)}

    async def get_image(self, image_id: str) -> Optional[Dict]:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM images WHERE image_id=$1", image_id)
        return dict(row) if row else None

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
            result.append(d)
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
