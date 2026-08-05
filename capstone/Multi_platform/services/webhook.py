import json
import hashlib
from datetime import datetime
from typing import Tuple

from capstone.Multi_platform.core.database import get_db
from capstone.Multi_platform.services.fake_social import FakeSocialPlatformServer

class WebhookHandler:
    def receive(self, payload_str: str, signature: str) -> Tuple[bool, str]:
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
        with get_db() as conn:
            existing = conn.execute(
                "SELECT * FROM webhook_events WHERE event_id=?", (event_id,)
            ).fetchone()
            if existing and existing["processed"]:
                return True, "Duplicate webhook — already processed"

            conn.execute("""
                INSERT OR IGNORE INTO webhook_events
                (event_id, post_id, platform, event_type, payload, signature_valid)
                VALUES (?,?,?,?,?,1)
            """, (event_id, post_id, platform, event_type, payload_str))

            if post_id and event_type == "post.published":
                conn.execute(
                    "UPDATE platform_posts SET status='published', published_at=? WHERE external_post_id=? OR post_id=?",
                    (datetime.utcnow().isoformat(), post_id, post_id)
                )

            conn.execute(
                "UPDATE webhook_events SET processed=1 WHERE event_id=?", (event_id,)
            )
            conn.commit()

        return True, f"Webhook processed: {event_type} for {post_id}"
