import json
import logging
import asyncio
import os
import traceback
from datetime import datetime
import redis.asyncio as redis

from capstone.Multi_platform.core.database import get_db_pool
from capstone.Multi_platform.services.publishers import PublisherAdapterFactory

logger = logging.getLogger(__name__)

redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)

async def start_worker():
    """Durable worker that pulls from Redis queue."""
    logger.info("Starting Multi_platform durable worker...")
    while True:
        try:
            # BRPOP blocks until an item is available
            result = await redis_client.brpop("campaign_queue", timeout=5)
            if result:
                _, message = result
                data = json.loads(message)
                campaign_id = data.get("campaign_id")
                
                # Check DB for campaign
                pool = await get_db_pool()
                async with pool.acquire() as conn:
                    # Get pending posts for this campaign
                    posts = await conn.fetch("SELECT * FROM platform_posts WHERE campaign_id=$1 AND status='queued'", campaign_id)
                
                if not posts:
                    continue
                
                for post in posts:
                    platform = post["platform"]
                    caption = post["caption"]
                    variant_path = post["image_variant_path"]
                    idem_key = post["idempotency_key"]
                    post_id = post["post_id"]
                    
                    try:
                        adapter = await PublisherAdapterFactory.get(platform)
                        # The adapter itself handles 429 backoff and 3 retries
                        success, msg, ext_post_id = await adapter.publish(caption, variant_path, idem_key)
                        
                        status = "published" if success else "failed"
                        # Actually wait, PDF says "Status only changes on a signature-verified webhook".
                        # But adapter returns 200/201 which means "platform accepted the post".
                        # It should probably go to "publishing" instead of "published" until webhook comes.
                        # Wait, original implementation sets it to "published" or "failed".
                        # The webhook says "event_type == 'post.published'".
                        # Let's set it to 'publishing' if success, else 'failed'.
                        new_status = "publishing" if success else "failed"
                        
                        async with pool.acquire() as conn:
                            await conn.execute("""
                                UPDATE platform_posts
                                SET status=$1, external_post_id=$2, publish_attempts=publish_attempts+1, last_error=$3
                                WHERE post_id=$4
                            """, new_status, ext_post_id, None if success else msg, post_id)
                    except Exception as e:
                        logger.error(f"Worker failed publishing post {post_id}: {traceback.format_exc()}")
                        async with pool.acquire() as conn:
                            await conn.execute("""
                                UPDATE platform_posts
                                SET status='failed', publish_attempts=publish_attempts+1, last_error=$1
                                WHERE post_id=$2
                            """, str(e), post_id)
                
                # Update campaign status
                async with pool.acquire() as conn:
                    all_posts = await conn.fetch("SELECT status FROM platform_posts WHERE campaign_id=$1", campaign_id)
                    statuses = [p["status"] for p in all_posts]
                    if all(s in ("published", "already_published (idempotent)") for s in statuses):
                        c_status = "published"
                    elif any(s in ("publishing", "queued") for s in statuses):
                        c_status = "publishing"
                    else:
                        c_status = "partial"
                        
                    await conn.execute("UPDATE campaigns SET status=$1, updated_at=$2 WHERE campaign_id=$3", c_status, datetime.utcnow().isoformat(), campaign_id)
                    
        except asyncio.CancelledError:
            logger.info("Worker cancelled, shutting down gracefully...")
            break
        except Exception as e:
            logger.error(f"Worker exception: {e}")
            await asyncio.sleep(5)
