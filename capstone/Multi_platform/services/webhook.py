import json
import hashlib
from datetime import datetime
from typing import Tuple

from capstone.Multi_platform.core.database import get_db_pool
from capstone.Multi_platform.services.fake_social import FakeSocialPlatformServer

class WebhookHandler:
    async def receive(self, payload_str: str, signature: str) -> Tuple[bool, str]:
        if not FakeSocialPlatformServer.verify_webhook_signature(payload_str, signature):
            return False, "Invalid HMAC signature — webhook rejected"

        try:
            payload = json.loads(payload_str)
        except json.JSONDecodeError:
            return False, "Invalid JSON payload"

        post_id = payload.get("post_id")
        event_type = payload.get("event", "unknown")
        platform = payload.get("platform", "unknown")

        event_id = f"wh_{hashlib.md5(payload_str.encode()).hexdigest()[:8]}"
        
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            existing = await conn.fetchrow(
                "SELECT * FROM webhook_events WHERE event_id=$1", event_id
            )
            if existing and existing["processed"]:
                return True, "Duplicate webhook — already processed"

            await conn.execute("""
                INSERT INTO webhook_events
                (event_id, post_id, platform, event_type, payload, signature_valid)
                VALUES ($1,$2,$3,$4,$5,TRUE)
                ON CONFLICT (event_id) DO NOTHING
            """, event_id, post_id, platform, event_type, payload_str)

            if post_id and event_type == "post.published":
                # Check which campaign it belongs to update campaign status if needed
                await conn.execute(
                    "UPDATE platform_posts SET status='published', published_at=$1 WHERE external_post_id=$2 OR post_id=$3",
                    datetime.utcnow().isoformat(), post_id, post_id
                )
                
                # Fetch campaign_id
                post_row = await conn.fetchrow("SELECT campaign_id FROM platform_posts WHERE external_post_id=$1 OR post_id=$2", post_id, post_id)
                if post_row:
                    camp_id = post_row["campaign_id"]
                    all_posts = await conn.fetch("SELECT status FROM platform_posts WHERE campaign_id=$1", camp_id)
                    statuses = [p["status"] for p in all_posts]
                    if all(s in ("published", "already_published (idempotent)") for s in statuses):
                        await conn.execute("UPDATE campaigns SET status='published', updated_at=$1 WHERE campaign_id=$2", datetime.utcnow().isoformat(), camp_id)

            await conn.execute(
                "UPDATE webhook_events SET processed=TRUE WHERE event_id=$1", event_id
            )

        return True, f"Webhook processed: {event_type} for {post_id}"
