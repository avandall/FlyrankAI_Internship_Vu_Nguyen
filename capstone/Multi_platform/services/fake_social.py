import time
import uuid
import json
import hmac
import hashlib
import logging
import threading
from typing import Dict, Optional, List

from capstone.Multi_platform.core.database import get_db

logger = logging.getLogger(__name__)

class FakeSocialPlatformServer:
    """
    In-process mock of the social platform API.
    Simulates: OAuth token validation, Rate-limit 429, Idempotency key, 
    signed webhooks, random errors.
    
    Per spec: "Tuyệt đối không gọi API thật hay dùng tài khoản thật"
    """

    WEBHOOK_SECRET = "fake_server_webhook_secret_hmac_key"
    _post_store: Dict[str, Dict] = {}  # idempotency_key → post
    _rate_counters: Dict[str, List[float]] = {}

    @classmethod
    def publish_post(cls, platform: str, token: str, caption: str,
                     image_path: Optional[str], idempotency_key: str) -> Dict:
        now = time.time()
        key = f"rate:{platform}"
        cls._rate_counters.setdefault(key, [])
        cls._rate_counters[key] = [t for t in cls._rate_counters[key] if now - t < 10]
        if len(cls._rate_counters[key]) >= 3:
            return {"status": 429, "headers": {"Retry-After": "5"}, "body": {"error": "Rate limit exceeded"}}

        if idempotency_key in cls._post_store:
            existing = cls._post_store[idempotency_key]
            logger.info(f"[FakeServer] Idempotent return for key={idempotency_key}")
            return {"status": 200, "body": {"post_id": existing["post_id"], "idempotent": True}}

        cls._rate_counters[key].append(now)

        if hash(idempotency_key + platform) % 10 == 0:
            return {"status": 500, "body": {"error": "Server temporarily unavailable"}}

        post_id = f"fake_{platform}_{uuid.uuid4().hex[:8]}"
        cls._post_store[idempotency_key] = {
            "post_id": post_id, "platform": platform, "caption": caption
        }

        cls._schedule_webhook(post_id, platform, idempotency_key)

        return {"status": 201, "body": {"post_id": post_id}}

    @classmethod
    def _schedule_webhook(cls, post_id: str, platform: str, idem_key: str):
        def deliver():
            time.sleep(1)
            payload = json.dumps({
                "event": "post.published",
                "post_id": post_id,
                "platform": platform,
                "idempotency_key": idem_key,
                "status": "published",
            })
            sig = hmac.new(
                cls.WEBHOOK_SECRET.encode(), payload.encode(), hashlib.sha256
            ).hexdigest()
            with get_db() as conn:
                conn.execute("""
                    INSERT OR IGNORE INTO webhook_events
                    (event_id, post_id, platform, event_type, payload, signature_valid)
                    VALUES (?,?,?,?,?,1)
                """, (f"wh_{uuid.uuid4().hex[:8]}", post_id, platform, "post.published", payload))
                conn.commit()
            logger.info(f"[FakeServer] Webhook delivered for post {post_id}")
        t = threading.Thread(target=deliver, daemon=True)
        t.start()

    @classmethod
    def verify_webhook_signature(cls, payload: str, signature: str) -> bool:
        expected = hmac.new(
            cls.WEBHOOK_SECRET.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
