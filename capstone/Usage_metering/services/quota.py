import uuid
import json
import logging
from typing import Optional, Dict

from capstone.Usage_metering.core.database import get_db_pool
from capstone.Usage_metering.core.exceptions import QuotaExceededError, PaymentRequiredError
from capstone.Usage_metering.core.config import DEFAULT_PLANS
from capstone.Usage_metering.services.tenant import TenantService
from capstone.Usage_metering.services.cost import CostCalculator

logger = logging.getLogger(__name__)

class QuotaService:
    def __init__(self):
        self.calc = CostCalculator()
        self.tenant_svc = TenantService()

    async def check_and_consume(
        self,
        tenant_id: str,
        event_type: str,
        quantity: int,
        idempotency_key: str,
        token_type: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict:
        tenant = await self.tenant_svc.get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant not found: {tenant_id}")

        pool = await get_db_pool()

        # Execute using a transaction to prevent race conditions around quota checks
        async with pool.acquire() as conn:
            async with conn.transaction():
                # 1. Idempotency check
                existing = await conn.fetchrow(
                    "SELECT * FROM usage_events WHERE idempotency_key=$1", idempotency_key
                )
                if existing:
                    logger.info(f"Idempotent event returned for key={idempotency_key}")
                    return {**dict(existing), "idempotent": True}

                # 2. Subscription status check (402)
                if tenant.get("subscription_status") not in ("active", None, ""):
                    if tenant["subscription_status"] in ("canceled", "past_due", "unpaid"):
                        raise PaymentRequiredError(
                            f"Subscription {tenant['subscription_status']} — upgrade required"
                        )

                # 3. Quota check (429)
                plan_config = DEFAULT_PLANS.get(tenant.get("plan", "free"), DEFAULT_PLANS["free"])
                row = await conn.fetchrow("""
                    SELECT COALESCE(SUM(quantity), 0) as total
                    FROM usage_events
                    WHERE tenant_id=$1 AND event_type=$2
                """, tenant_id, event_type)
                current_usage = row["total"] if row else 0

                quota_key = "quota_api_calls" if event_type == "api_call" else "quota_ai_tokens"
                quota_limit = plan_config[quota_key]

                # Boundary check: current + new must be ≤ quota
                if current_usage + quantity > quota_limit:
                    raise QuotaExceededError(
                        f"Quota exceeded: {current_usage + quantity}/{quota_limit} {event_type} "
                        f"(plan={tenant['plan']}). Upgrade to increase quota."
                    )

                # 4. Calculate cost
                if event_type == "ai_tokens" and token_type:
                    cost = self.calc.calculate_ai_cost(token_type, quantity)
                else:
                    cost = self.calc.calculate_api_call_cost(quantity)

                # 5. Record event
                event_id = f"evt_{uuid.uuid4().hex[:10]}"
                await conn.execute("""
                    INSERT INTO usage_events
                    (event_id, idempotency_key, tenant_id, event_type, quantity,
                     token_type, cost_micro_cents, metadata)
                    VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
                """, event_id, idempotency_key, tenant_id, event_type, quantity,
                     token_type, cost, json.dumps(metadata or {}))

        return {
            "event_id": event_id,
            "tenant_id": tenant_id,
            "event_type": event_type,
            "quantity": quantity,
            "token_type": token_type,
            "cost_micro_cents": cost,
            "cost_display": self.calc.micro_cents_to_display(cost),
            "idempotent": False,
        }

    async def _get_current_usage(self, tenant_id: str, event_type: str) -> int:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT COALESCE(SUM(quantity), 0) as total
                FROM usage_events
                WHERE tenant_id=$1 AND event_type=$2
            """, tenant_id, event_type)
        return row["total"] if row else 0

    async def get_usage_summary(self, tenant_id: str) -> Dict:
        tenant = await self.tenant_svc.get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant not found: {tenant_id}")

        plan_config = DEFAULT_PLANS.get(tenant["plan"], DEFAULT_PLANS["free"])
        api_usage = await self._get_current_usage(tenant_id, "api_call")
        token_usage = await self._get_current_usage(tenant_id, "ai_tokens")

        return {
            "tenant_id": tenant_id,
            "plan": tenant["plan"],
            "subscription_status": tenant.get("subscription_status", "active"),
            "api_calls": {
                "used": api_usage,
                "limit": plan_config["quota_api_calls"],
                "remaining": max(0, plan_config["quota_api_calls"] - api_usage),
                "pct": round(api_usage / plan_config["quota_api_calls"] * 100, 1) if plan_config["quota_api_calls"] else 0,
            },
            "ai_tokens": {
                "used": token_usage,
                "limit": plan_config["quota_ai_tokens"],
                "remaining": max(0, plan_config["quota_ai_tokens"] - token_usage),
                "pct": round(token_usage / plan_config["quota_ai_tokens"] * 100, 1) if plan_config["quota_ai_tokens"] else 0,
            },
        }
