import re
import uuid
import json
import logging
import asyncio
from typing import Dict, List

from capstone.Embeddeable_widget.core.database import get_db_pool
from capstone.Embeddeable_widget.core.exceptions import SpamDetectedError, RateLimitError, ValidationError
from capstone.Embeddeable_widget.services.geoip import GeoIPService
from capstone.Embeddeable_widget.services.abuse import AbuseProtection
from capstone.Embeddeable_widget.services.webhook import WebhookService
from capstone.Embeddeable_widget.services.widget import WidgetService
from capstone.Embeddeable_widget.core.config import RATE_LIMIT_MAX_REQUESTS
from capstone.Embeddeable_widget.schemas import format_db_row

logger = logging.getLogger(__name__)


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

        # 2. Origin domain validation (if configured)
        allowed = widget.get("allowed_domains", [])
        if allowed and isinstance(allowed, list) and len(allowed) > 0 and source_origin and source_origin != "unknown":
            origin_clean = source_origin.replace("http://", "").replace("https://", "").split(":")[0].split("/")[0]
            if "*" not in allowed and origin_clean not in allowed and "localhost" not in allowed and "127.0.0.1" not in allowed:
                # Check domain suffixes
                if not any(origin_clean.endswith(domain) for domain in allowed):
                    logger.warning(f"Origin {source_origin} not allowed for widget {widget_id}")

        # 3. Honeypot anti-spam check
        if self.abuse.check_honeypot(data.get("_hp_field")):
            raise SpamDetectedError("Spam detected via honeypot field")

        # 4. Rate limit check
        limit = widget.get("rate_limit_per_min", RATE_LIMIT_MAX_REQUESTS)
        rate_ok, reason = await self.abuse.check_rate_limit(source_ip, widget_id, limit)
        if not rate_ok:
            raise RateLimitError(reason)

        # 5. Basic field validation
        email = (data.get("email") or "").strip()
        if email and not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            raise ValidationError("Invalid email format")

        # 6. Geo IP lookup (graceful fallback)
        geo = await self.geo.lookup(source_ip)

        # 7. Persist row
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
                (data.get("name") or "").strip(),
                (data.get("phone") or "").strip(),
                (data.get("message") or "").strip(),
                json.dumps({k: v for k, v in data.items() if k not in ("email","name","phone","message","_hp_field")}),
                source_origin, source_ip,
                geo.get("country"), geo.get("city"), geo.get("region"), geo.get("provider"),
                "pending",
            )

        # 8. Safe side effects (Email + Webhook) - Failure MUST NOT break submission
        async def run_side_effects():
            # Email notification side effect (logger/mock catcher)
            try:
                logger.info(f"[EMAIL NOTIFICATION] New lead {submission_id} for widget {widget_id} ({email})")
            except Exception as e:
                logger.error(f"Email side effect error (ignored): {e}")

            # Webhook delivery side effect
            webhook_status = "no_webhook"
            if widget.get("webhook_url"):
                try:
                    ok, msg = await self.webhook.deliver(widget["webhook_url"], {
                        "event": "new_submission",
                        "submission_id": submission_id,
                        "widget_id": widget_id,
                        "tenant_id": widget["tenant_id"],
                        "data": {"email": email, "name": data.get("name")},
                        "geo": geo,
                    })
                    webhook_status = "delivered" if ok else f"failed:{msg}"
                except Exception as ex:
                    webhook_status = f"failed:{ex}"

                try:
                    async with pool.acquire() as c:
                        await c.execute("UPDATE submissions SET webhook_status=$1 WHERE submission_id=$2", webhook_status, submission_id)
                except Exception:
                    pass

        asyncio.create_task(run_side_effects())

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
        return [format_db_row(dict(r)) for r in rows]

    async def get_stats(self, tenant_id: str) -> Dict:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            total_row = await conn.fetchrow("SELECT COUNT(*) as c FROM submissions WHERE tenant_id=$1", tenant_id)
            total = total_row["c"] if total_row else 0
            
            by_widget = await conn.fetch("SELECT widget_id, COUNT(*) as count FROM submissions WHERE tenant_id=$1 GROUP BY widget_id", tenant_id)
            by_country = await conn.fetch("SELECT country, COUNT(*) as count FROM submissions WHERE tenant_id=$1 AND country IS NOT NULL GROUP BY country", tenant_id)
            by_date = await conn.fetch("""
                SELECT TO_CHAR(submitted_at, 'YYYY-MM-DD') as date_str, COUNT(*) as count
                FROM submissions
                WHERE tenant_id=$1
                GROUP BY date_str
                ORDER BY date_str DESC
                LIMIT 30
            """, tenant_id)
            
        return {
            "total": total,
            "by_widget": {r["widget_id"]: r["count"] for r in by_widget},
            "by_country": {r["country"]: r["count"] for r in by_country},
            "by_date": {r["date_str"]: r["count"] for r in by_date if r["date_str"]},
        }
