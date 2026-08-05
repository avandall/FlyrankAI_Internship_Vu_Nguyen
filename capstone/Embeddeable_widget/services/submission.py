import re
import uuid
import json
import asyncio
from typing import Dict, List

from capstone.Embeddeable_widget.core.database import get_db_pool
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

    async def submit(
        self,
        widget_id: str,
        data: Dict,
        source_ip: str,
        source_origin: str,
    ) -> Dict:
        # 1. Load widget
        widget = await self.widgets.get_widget(widget_id)
        if not widget:
            raise ValueError(f"Widget not found: {widget_id}")
        if not widget.get("is_active", True):
            raise ValueError("Widget is disabled")

        # 2. Honeypot anti-spam
        if self.abuse.check_honeypot(data.get("_hp_field")):
            raise SpamDetectedError("Spam detected via honeypot field")

        # 3. Rate limit
        limit = widget.get("rate_limit_per_min", RATE_LIMIT_MAX_REQUESTS)
        allowed, reason = await self.abuse.check_rate_limit(source_ip, widget_id, limit)
        if not allowed:
            raise RateLimitError(reason)

        # 4. Basic field validation
        email = data.get("email", "").strip()
        if email and not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            raise ValidationError("Invalid email format")

        # 5. Geo IP (safe — won't raise on failure)
        geo = await self.geo.lookup(source_ip)

        # 6. Persist
        submission_id = f"sub_{uuid.uuid4().hex[:12]}"
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO submissions (
                    submission_id, widget_id, tenant_id, email, name, phone, message,
                    custom_fields, source_origin, source_ip, country, city, region, geo_provider,
                    webhook_status
                ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15)
            """,
                submission_id, widget_id, widget["tenant_id"],
                email,
                data.get("name", "").strip(),
                data.get("phone", "").strip(),
                data.get("message", "").strip(),
                json.dumps({k: v for k, v in data.items() if k not in ("email","name","phone","message","_hp_field")}),
                source_origin, source_ip,
                geo.get("country"), geo.get("city"), geo.get("region"), geo.get("provider"),
                "pending",
            )

        # 7. Webhook (safe side effect) - Fire and forget
        async def send_webhook():
            webhook_status = "no_webhook"
            if widget.get("webhook_url"):
                ok, msg = await self.webhook.deliver(widget["webhook_url"], {
                    "event": "new_submission",
                    "submission_id": submission_id,
                    "widget_id": widget_id,
                    "tenant_id": widget["tenant_id"],
                    "data": {"email": email, "name": data.get("name")},
                    "geo": geo,
                })
                webhook_status = "delivered" if ok else f"failed:{msg}"
                async with pool.acquire() as c:
                    await c.execute("UPDATE submissions SET webhook_status=$1 WHERE submission_id=$2", webhook_status, submission_id)

        asyncio.create_task(send_webhook())

        return {
            "submission_id": submission_id,
            "widget_id": widget_id,
            "email": email,
            "country": geo.get("country"),
            "city": geo.get("city"),
            "geo_provider": geo.get("provider"),
            "webhook_status": "pending",
        }

    async def get_for_tenant(self, tenant_id: str, limit: int = 100) -> List[Dict]:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM submissions WHERE tenant_id=$1 ORDER BY submitted_at DESC LIMIT $2", tenant_id, limit)
        return [dict(r) for r in rows]

    async def get_stats(self, tenant_id: str) -> Dict:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            total_row = await conn.fetchrow("SELECT COUNT(*) as c FROM submissions WHERE tenant_id=$1", tenant_id)
            total = total_row["c"] if total_row else 0
            
            by_widget = await conn.fetch("SELECT widget_id, COUNT(*) as count FROM submissions WHERE tenant_id=$1 GROUP BY widget_id", tenant_id)
            by_country = await conn.fetch("SELECT country, COUNT(*) as count FROM submissions WHERE tenant_id=$1 AND country IS NOT NULL GROUP BY country", tenant_id)
            
        return {
            "total": total,
            "by_widget": {r["widget_id"]: r["count"] for r in by_widget},
            "by_country": {r["country"]: r["count"] for r in by_country},
        }
