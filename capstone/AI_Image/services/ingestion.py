import uuid
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from capstone.AI_Image.core.database import get_db
from capstone.AI_Image.utils import compute_embedding, call_vision_ai
from capstone.AI_Image.core.config import CONFIDENCE_THRESHOLD

logger = logging.getLogger(__name__)

class ImageIngestionService:
    """Handles file upload → Vision AI → embedding → DB storage pipeline."""

    def ingest_from_file(
        self,
        filename: str,
        file_bytes: bytes,
        image_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Full ingest pipeline:
        1. Create batch job record
        2. Call Vision AI (real or simulated)
        3. Generate semantic embedding
        4. Store in DB with flagging if low confidence
        5. Update job status + cost tracking
        """
        image_id = image_id or f"img_{uuid.uuid4().hex[:10]}"
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        
        with get_db() as conn:
            conn.execute(
                "INSERT INTO ingest_jobs (job_id, image_id, status) VALUES (?, ?, 'queued')",
                (job_id, image_id)
            )
            conn.commit()
        
        try:
            # Simulate processing time
            with get_db() as conn:
                conn.execute(
                    "UPDATE ingest_jobs SET status='processing', updated_at=? WHERE job_id=?",
                    (datetime.utcnow().isoformat(), job_id)
                )
                conn.commit()
            
            # --- Step 1: Vision AI analysis ---
            vision_result = call_vision_ai(filename, file_bytes)
            
            # --- Step 2: Generate semantic embedding ---
            embed_text = f"{vision_result['caption']} {vision_result['subject']} {' '.join(vision_result['attributes'])}"
            embedding = compute_embedding(embed_text)
            
            # --- Step 3: Flagging ---
            is_flagged = vision_result["confidence_score"] < CONFIDENCE_THRESHOLD
            if is_flagged:
                logger.warning(f"Image {image_id} flagged: confidence={vision_result['confidence_score']:.2f}")
            
            # Try to get image dimensions
            width, height = None, None
            try:
                from PIL import Image as PILImage
                import io
                img = PILImage.open(io.BytesIO(file_bytes))
                width, height = img.size
            except Exception:
                width, height = 0, 0
            
            # --- Step 4: Persist to DB ---
            with get_db() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO images
                    (image_id, filename, file_size_bytes, format, width, height,
                     subject, category, attributes, caption, confidence_score,
                     is_flagged, embedding)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    image_id, filename, len(file_bytes),
                    Path(filename).suffix.lstrip(".").lower(),
                    width, height,
                    vision_result["subject"], vision_result["category"],
                    json.dumps(vision_result["attributes"]),
                    vision_result["caption"],
                    vision_result["confidence_score"],
                    1 if is_flagged else 0,
                    json.dumps(embedding),
                ))
                conn.execute("""
                    UPDATE ingest_jobs
                    SET status='done', ai_cost_micro_usd=?, updated_at=?
                    WHERE job_id=?
                """, (vision_result["ai_cost_micro_usd"], datetime.utcnow().isoformat(), job_id))
                conn.commit()
            
            return {
                "image_id": image_id,
                "job_id": job_id,
                "filename": filename,
                "subject": vision_result["subject"],
                "category": vision_result["category"],
                "caption": vision_result["caption"],
                "confidence_score": vision_result["confidence_score"],
                "is_flagged": is_flagged,
                "ai_cost_micro_usd": vision_result["ai_cost_micro_usd"],
                "model_used": vision_result["model_used"],
            }
        
        except Exception as exc:
            with get_db() as conn:
                conn.execute(
                    "UPDATE ingest_jobs SET status='failed', error_msg=?, updated_at=? WHERE job_id=?",
                    (str(exc), datetime.utcnow().isoformat(), job_id)
                )
                conn.commit()
            raise

    def ingest_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Direct metadata ingest (for seeding without file upload)."""
        embedding = compute_embedding(
            f"{metadata['caption']} {metadata['subject']} {' '.join(metadata.get('attributes', []))}"
        )
        is_flagged = metadata.get("confidence_score", 1.0) < CONFIDENCE_THRESHOLD
        
        with get_db() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO images
                (image_id, filename, file_size_bytes, format, width, height,
                 subject, category, attributes, caption, confidence_score, is_flagged, embedding)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                metadata["image_id"], metadata["filename"],
                metadata.get("file_size_bytes", 0), metadata.get("format", "jpg"),
                metadata.get("width"), metadata.get("height"),
                metadata["subject"], metadata["category"],
                json.dumps(metadata.get("attributes", [])),
                metadata["caption"], metadata.get("confidence_score", 0.9),
                1 if is_flagged else 0,
                json.dumps(embedding),
            ))
            conn.commit()
        
        return {**metadata, "is_flagged": is_flagged, "embedding_dim": len(embedding)}

    def get_image(self, image_id: str) -> Optional[Dict]:
        with get_db() as conn:
            row = conn.execute("SELECT * FROM images WHERE image_id=?", (image_id,)).fetchone()
        return dict(row) if row else None

    def get_all_images(self) -> List[Dict]:
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM images ORDER BY created_at DESC").fetchall()
        result = []
        for row in rows:
            d = dict(row)
            if d.get("attributes"):
                d["attributes"] = json.loads(d["attributes"])
            d.pop("embedding", None)  # Don't expose raw embedding in list
            result.append(d)
        return result

    def get_job_status(self, job_id: str) -> Optional[Dict]:
        with get_db() as conn:
            row = conn.execute("SELECT * FROM ingest_jobs WHERE job_id=?", (job_id,)).fetchone()
        return dict(row) if row else None

    def get_cost_summary(self) -> Dict[str, Any]:
        with get_db() as conn:
            rows = conn.execute("""
                SELECT status, COUNT(*) as count, SUM(ai_cost_micro_usd) as total_cost
                FROM ingest_jobs GROUP BY status
            """).fetchall()
        summary = {row["status"]: {"count": row["count"], "cost_micro_usd": row["total_cost"] or 0} for row in rows}
        total = sum(v["cost_micro_usd"] for v in summary.values())
        return {"by_status": summary, "total_cost_micro_usd": total, "total_cost_usd": f"${total/1_000_000:.6f}"}
