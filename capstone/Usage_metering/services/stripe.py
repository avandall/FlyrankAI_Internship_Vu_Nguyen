import hmac
import hashlib
import json
import uuid
from typing import Tuple, Dict
from datetime import datetime, timezone

from capstone.Usage_metering.core.config import STRIPE_WEBHOOK_SECRET
from capstone.Usage_metering.core.database import get_db
from capstone.Usage_metering.services.tenant import TenantService

class StripeWebhookHandler:
    def verify_signature(self, payload: str, stripe_signature: str) -> bool:
        try:
            parts = dict(p.split("=", 1) for p in stripe_signature.split(","))
            timestamp = parts.get("t", "")
            sig = parts.get("v1", "")

            signed_payload = f"{timestamp}.{payload}"
            expected = hmac.new(
                STRIPE_WEBHOOK_SECRET.encode(),
                signed_payload.encode(),
                hashlib.sha256,
            ).hexdigest()

            return hmac.compare_digest(expected, sig)
        except Exception:
            return False

    def process(self, payload_str: str, stripe_signature: str) -> Tuple[bool, str, Dict]:
        if not self.verify_signature(payload_str, stripe_signature):
            return False, "Invalid Stripe webhook signature", {}

        try:
            payload = json.loads(payload_str)
        except Exception:
            return False, "Invalid JSON", {}

        event_id = payload.get("id", uuid.uuid4().hex)
        event_type = payload.get("type", "")

        with get_db() as conn:
            existing = conn.execute(
                "SELECT * FROM stripe_events WHERE stripe_event_id=? AND processed=1",
                (event_id,)
            ).fetchone()
            if existing:
                return True, f"Duplicate event {event_id} — already processed", {}

        result = {}
        tenant_svc = TenantService()

        if event_type == "checkout.session.completed":
            obj = payload.get("data", {}).get("object", {})
            customer_id = obj.get("customer")
            sub_id = obj.get("subscription")
            metadata = obj.get("metadata", {})
            tenant_id = metadata.get("tenant_id")

            if tenant_id:
                with get_db() as conn:
                    conn.execute("""
                        UPDATE tenants SET stripe_customer_id=?, stripe_subscription_id=?,
                            subscription_status='active', plan='pro'
                        WHERE tenant_id=?
                    """, (customer_id, sub_id, tenant_id))
                    conn.commit()
                result = {"tenant_id": tenant_id, "new_plan": "pro", "action": "upgraded"}

        elif event_type == "customer.subscription.updated":
            obj = payload.get("data", {}).get("object", {})
            sub_id = obj.get("id")
            status = obj.get("status")
            with get_db() as conn:
                row = conn.execute(
                    "SELECT * FROM tenants WHERE stripe_subscription_id=?", (sub_id,)
                ).fetchone()
                if row:
                    conn.execute(
                        "UPDATE tenants SET subscription_status=? WHERE tenant_id=?",
                        (status, row["tenant_id"])
                    )
                    conn.commit()
                    result = {"tenant_id": row["tenant_id"], "new_status": status}

        elif event_type == "customer.subscription.deleted":
            obj = payload.get("data", {}).get("object", {})
            sub_id = obj.get("id")
            with get_db() as conn:
                row = conn.execute(
                    "SELECT * FROM tenants WHERE stripe_subscription_id=?", (sub_id,)
                ).fetchone()
                if row:
                    conn.execute("""
                        UPDATE tenants SET plan='free', subscription_status='canceled',
                            stripe_subscription_id=NULL
                        WHERE tenant_id=?
                    """, (row["tenant_id"],))
                    conn.commit()
                    result = {"tenant_id": row["tenant_id"], "action": "downgraded_to_free"}

        with get_db() as conn:
            conn.execute("""
                INSERT OR IGNORE INTO stripe_events
                (stripe_event_id, event_type, payload, processed, processed_at)
                VALUES (?,?,?,1,?)
            """, (event_id, event_type, payload_str, datetime.now(timezone.utc).isoformat()))
            conn.commit()

        return True, f"Processed: {event_type}", result
