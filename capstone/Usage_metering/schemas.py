"""
Schemas for Usage Metering & Billing Engine.
"""

from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class PlanTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class UsageEvent(BaseModel):
    idempotency_key: str
    tenant_id: str
    event_type: str  # e.g., "llm_inference"
    input_tokens: int = Field(default=0, ge=0)
    cached_input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    reasoning_tokens: int = Field(default=0, ge=0)
    timestamp: int


class PlanLimits(BaseModel):
    plan_tier: PlanTier
    max_requests_per_month: int
    max_tokens_per_month: int
    overage_allowed: bool = False


class QuotaCheckResult(BaseModel):
    tenant_id: str
    allowed: bool
    current_requests: int
    max_requests: int
    current_tokens: int
    max_tokens: int
    rejection_reason: Optional[str] = None


class CostBreakdown(BaseModel):
    input_cost_micro_cents: int
    cached_input_cost_micro_cents: int
    output_cost_micro_cents: int
    reasoning_cost_micro_cents: int
    total_cost_micro_cents: int
    total_cost_usd_formatted: str


class InvoiceSnapshot(BaseModel):
    invoice_id: str
    tenant_id: str
    plan_tier: PlanTier
    total_events: int
    total_tokens: int
    total_amount_micro_cents: int
    total_amount_usd: str
    status: str = "draft"
