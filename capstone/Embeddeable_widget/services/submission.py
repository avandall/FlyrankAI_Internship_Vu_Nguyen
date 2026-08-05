import re
import uuid
import json
from typing import Dict, List

from capstone.Embeddeable_widget.core.database import get_db
from capstone.Embeddeable_widget.core.exceptions import SpamDetectedError, RateLimitError, ValidationError
from capstone.Embeddeable_widget.services.geoip import GeoIPService
from capstone.Embeddeable_widget.services.abuse import AbuseProtection
from capstone.Embeddeable_widget.services.webhook import WebhookService
from capstone.Embeddeable_widget.services.widget import WidgetService
from capstone.Embeddeable_widget.core.config import RATE_LIMIT_MAX_REQUESTS

class SubmissionService:
    def __init__(self):
        self.geo = GeoIPService()
        self.abuse = AbuseProtection()
        self.webhook = WebhookService()
        self.widgets = WidgetService()

    def submit(
        self,
        widget_id: str,
        data: Dict,
        source_ip: str,
        source_origin: str,
    ) -> Dict:
        """
        Full submission pipeline:
        1. Load widget config
        2. Honeypot check (spam)
        3. Rate limit check per IP + widget
        4. Validate required fields
        5. Geo IP enrichment (fallback-safe)
        6. Persist submission
        7. Deliver webhook (safe side effect)
        """
        # 1. Load widget
        widget = self.widgets.get_widget(widget_id)
        if not widget:
            raise ValueError(f"Widget not found: {widget_id}")
        if not widget.get("is_active", True):
            raise ValueError("Widget is disabled")

        # 2. Honeypot anti-spam
        if self.abuse.check_honeypot(data.get("_hp_field")):
            raise SpamDetectedError("Spam detected via honeypot field")

        # 3. Rate limit
        limit = widget.get("rate_limit_per_min", RATE_LIMIT_MAX_REQUESTS)
        allowed, reason = self.abuse.check_rate_limit(source_ip, widget_id, limit)
        if not allowed:
            raise RateLimitError(reason)

        # 4. Basic field validation
        email = data.get("email", "").strip()
        if email and not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            raise ValidationError("Invalid email format")

        # 5. Geo IP (safe — won't raise on failure)
        geo = self.geo.lookup(source_ip)

        # 6. Persist
        submission_id = f"sub_{uuid.uuid4().hex[:12]}"
        with get_db() as conn:
            conn.execute("""
                INSERT INTO submissions
                (submission_id, widget_id, tenant_id, email, name, phone, message,
                 custom_fields, source_origin, source_ip, country, city, region, geo_provider,
                 webhook_status)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                submission_id, widget_id, widget["tenant_id"],
                email,
                data.get("name", "").strip(),
                data.get("phone", "").strip(),
                data.get("message", "").strip(),
                json.dumps({k: v for k, v in data.items() if k not in ("email","name","phone","message","_hp_field")}),
                source_origin, source_ip,
                geo.get("country"), geo.get("city"), geo.get("region"), geo.get("provider"),
                "pending",
            ))
            conn.commit()

        # 7. Webhook (safe side effect)
        webhook_status = "no_webhook"
        if widget.get("webhook_url"):
            ok, msg = self.webhook.deliver(widget["webhook_url"], {
                "event": "new_submission",
                "submission_id": submission_id,
                "widget_id": widget_id,
                "tenant_id": widget["tenant_id"],
                "data": {"email": email, "name": data.get("name")},
                "geo": geo,
            })
            webhook_status = "delivered" if ok else f"failed:{msg}"
            with get_db() as conn:
                conn.execute(
                    "UPDATE submissions SET webhook_status=? WHERE submission_id=?",
                    (webhook_status, submission_id)
                )
                conn.commit()

        return {
            "submission_id": submission_id,
            "widget_id": widget_id,
            "email": email,
            "country": geo.get("country"),
            "city": geo.get("city"),
            "geo_provider": geo.get("provider"),
            "webhook_status": webhook_status,
        }

    def get_for_tenant(self, tenant_id: str, limit: int = 100) -> List[Dict]:
        with get_db() as conn:
            rows = conn.execute("""
                SELECT * FROM submissions WHERE tenant_id=?
                ORDER BY submitted_at DESC LIMIT ?
            """, (tenant_id, limit)).fetchall()
        return [dict(r) for r in rows]

    def get_stats(self, tenant_id: str) -> Dict:
        with get_db() as conn:
            total = conn.execute(
                "SELECT COUNT(*) as c FROM submissions WHERE tenant_id=?", (tenant_id,)
            ).fetchone()["c"]
            by_widget = conn.execute("""
                SELECT widget_id, COUNT(*) as count FROM submissions
                WHERE tenant_id=? GROUP BY widget_id
            """, (tenant_id,)).fetchall()
            by_country = conn.execute("""
                SELECT country, COUNT(*) as count FROM submissions
                WHERE tenant_id=? AND country IS NOT NULL GROUP BY country
            """, (tenant_id,)).fetchall()
        return {
            "total": total,
            "by_widget": {r["widget_id"]: r["count"] for r in by_widget},
            "by_country": {r["country"]: r["count"] for r in by_country},
        }
