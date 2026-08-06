import os
import json
import asyncio
import logging
from datetime import datetime
import redis.asyncio as redis
from capstone.AI_Image.core.database import get_db_pool
from capstone.AI_Image.utils import call_vision_ai, compute_embedding
from capstone.AI_Image.core.config import CONFIDENCE_THRESHOLD
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)

QUEUE_NAME = "image_ingestion_queue"
MAX_RETRIES = int(os.getenv("MAX_BATCH_RETRY", 3))

async def process_job(job_id: str, image_id: str, filename: str, file_bytes_b64: str):
    import base64
    file_bytes = base64.b64decode(file_bytes_b64)
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE ingest_jobs SET status=$1, updated_at=$2 WHERE job_id=$3",
            "processing", datetime.utcnow(), job_id
        )

    try:
        # Step 0: Save image file to static/uploads for preview serving
        uploads_dir = Path(os.path.dirname(__file__)) / "static" / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        (uploads_dir / filename).write_bytes(file_bytes)
        (uploads_dir / f"{image_id}_{filename}").write_bytes(file_bytes)

        # Step 1: Vision AI (with validation)
        vision_result = await call_vision_ai(filename, file_bytes)

        # Step 2: Semantic embedding
        embed_text = f"{vision_result['caption']} {vision_result['subject']} {' '.join(vision_result['attributes'])}"
        embedding = await compute_embedding(embed_text)

        # Step 3: Confidence flagging
        is_flagged = vision_result["confidence_score"] < CONFIDENCE_THRESHOLD

        # Extract dimensions if possible
        width, height = 0, 0
        try:
            from PIL import Image as PILImage
            import io
            img = PILImage.open(io.BytesIO(file_bytes))
            width, height = img.size
        except Exception:
            pass

        import base64
        from capstone.AI_Image.utils import compute_image_hashes
        file_hash, perceptual_hash = compute_image_hashes(file_bytes)
        file_bytes_b64 = base64.b64encode(file_bytes).decode('utf-8')

        # Step 4: Persist to Postgres
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("""
                    INSERT INTO images (
                        image_id, filename, file_size_bytes, format, width, height,
                        subject, category, attributes, caption, confidence_score,
                        is_flagged, embedding, file_hash, file_bytes_b64, perceptual_hash
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                    ON CONFLICT (image_id) DO UPDATE SET
                        subject=EXCLUDED.subject,
                        category=EXCLUDED.category,
                        attributes=EXCLUDED.attributes,
                        caption=EXCLUDED.caption,
                        confidence_score=EXCLUDED.confidence_score,
                        is_flagged=EXCLUDED.is_flagged,
                        embedding=EXCLUDED.embedding,
                        file_hash=EXCLUDED.file_hash,
                        file_bytes_b64=EXCLUDED.file_bytes_b64,
                        perceptual_hash=EXCLUDED.perceptual_hash
                """, 
                    image_id, filename, len(file_bytes),
                    Path(filename).suffix.lstrip(".").lower() or "jpg",
                    width, height,
                    vision_result["subject"], vision_result["category"],
                    json.dumps(vision_result["attributes"]),
                    vision_result["caption"],
                    vision_result["confidence_score"],
                    1 if is_flagged else 0,
                    json.dumps(embedding),
                    file_hash,
                    file_bytes_b64,
                    perceptual_hash
                )

                await conn.execute("""
                    UPDATE ingest_jobs
                    SET status='done', ai_cost_micro_usd=$1, updated_at=$2
                    WHERE job_id=$3
                """, vision_result["ai_cost_micro_usd"], datetime.utcnow(), job_id)
                
        logger.info(f"Successfully processed job {job_id} for image {image_id}")
        
    except Exception as exc:
        logger.error(f"Error processing job {job_id}: {exc}")
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT retries FROM ingest_jobs WHERE job_id=$1", job_id)
            retries = row['retries'] if row else 0
            if retries < MAX_RETRIES:
                await conn.execute(
                    "UPDATE ingest_jobs SET status='queued', retries=retries+1, updated_at=$1 WHERE job_id=$2",
                    datetime.utcnow(), job_id
                )
                # Re-queue
                await redis_client.rpush(QUEUE_NAME, json.dumps({
                    "job_id": job_id, "image_id": image_id, "filename": filename, "file_bytes_b64": file_bytes_b64
                }))
            else:
                await conn.execute(
                    "UPDATE ingest_jobs SET status='failed', error_msg=$1, updated_at=$2 WHERE job_id=$3",
                    str(exc), datetime.utcnow(), job_id
                )

async def worker_loop():
    logger.info("Worker started, waiting for jobs...")
    while True:
        try:
            # BLPOP waits for an item in the list
            result = await redis_client.blpop(QUEUE_NAME, timeout=1)
            if result:
                _, data_json = result
                data = json.loads(data_json)
                await process_job(
                    data["job_id"], data["image_id"], data["filename"], data["file_bytes_b64"]
                )
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Worker loop error: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(worker_loop())
