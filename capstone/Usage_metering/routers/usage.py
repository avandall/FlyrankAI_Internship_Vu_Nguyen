from fastapi import APIRouter, HTTPException
from capstone.Usage_metering.services.quota import QuotaService
from capstone.Usage_metering.services.cost import CostCalculator
from capstone.Usage_metering.core.config import TOKEN_PRICE_CONFIG, DEFAULT_PLANS
from capstone.Usage_metering.core.exceptions import QuotaExceededError, PaymentRequiredError

router = APIRouter(prefix="/api", tags=["Usage"])
quota_svc = QuotaService()
calc = CostCalculator()

@router.post("/usage/record", summary="Record a billable usage event")
def record_usage(body: dict):
    tenant_id = body.get("tenant_id", "")
    event_type = body.get("event_type", "api_call")
    quantity = body.get("quantity", 1)
    idempotency_key = body.get("idempotency_key", "")
    token_type = body.get("token_type")

    if not tenant_id or not idempotency_key:
        raise HTTPException(status_code=422, detail="tenant_id and idempotency_key required")
    if event_type not in ("api_call", "ai_tokens"):
        raise HTTPException(status_code=422, detail="event_type must be api_call or ai_tokens")
    if event_type == "ai_tokens" and token_type not in TOKEN_PRICE_CONFIG:
        raise HTTPException(status_code=422, detail=f"token_type must be one of: {list(TOKEN_PRICE_CONFIG)}")

    try:
        event = quota_svc.check_and_consume(
            tenant_id, event_type, quantity, idempotency_key,
            token_type=token_type,
            metadata=body.get("metadata"),
        )
        return {"status": "recorded", "event": event}
    except QuotaExceededError as e:
        raise HTTPException(
            status_code=429,
            detail=str(e),
            headers={"X-Quota-Exceeded": "true"},
        )
    except PaymentRequiredError as e:
        raise HTTPException(status_code=402, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/usage/{tenant_id}", summary="Get current usage and quota status")
def get_usage(tenant_id: str):
    try:
        return quota_svc.get_usage_summary(tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/invoice/{tenant_id}", summary="Get monthly invoice preview")
def get_invoice(tenant_id: str):
    try:
        return calc.monthly_invoice(tenant_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plans", summary="Available billing plans")
def get_plans():
    return {
        "plans": DEFAULT_PLANS,
        "token_pricing": TOKEN_PRICE_CONFIG,
        "pricing_unit": "micro_cents (1 micro-cent = $0.00000001)",
        "note": "All monetary values stored as integers (no floats)"
    }
