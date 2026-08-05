import json
import time
import hmac
import hashlib
from fastapi import APIRouter, HTTPException, Request

from capstone.Usage_metering.services.stripe import StripeWebhookHandler
from capstone.Usage_metering.core.config import STRIPE_WEBHOOK_SECRET

router = APIRouter(prefix="/api/webhook/stripe", tags=["Stripe Webhook"])
stripe_handler = StripeWebhookHandler()

@router.post("", summary="Stripe webhook endpoint (HMAC verified)")
async def stripe_webhook(request: Request):
    raw_body = await request.body()
    payload_str = raw_body.decode("utf-8")
    stripe_signature = request.headers.get("Stripe-Signature", "")

    success, message, result = stripe_handler.process(payload_str, stripe_signature)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"status": "ok", "message": message, "result": result}

@router.post("/test", summary="Simulate Stripe webhook (for testing)")
async def simulate_stripe_webhook(body: dict):
    event_type = body.get("event_type", "checkout.session.completed")
    tenant_id = body.get("tenant_id", "t_demo_free")
    forge = body.get("forge_signature", False)

    timestamp = str(int(time.time()))

    if event_type == "checkout.session.completed":
        payload_data = {
            "id": f"evt_{hash(event_type + tenant_id) % 10**10}",
            "type": event_type,
            "data": {
                "object": {
                    "customer": f"cus_test_{tenant_id}",
                    "subscription": f"sub_test_{tenant_id}",
                    "metadata": {"tenant_id": tenant_id},
                }
            }
        }
    elif event_type == "customer.subscription.deleted":
        payload_data = {
            "id": f"evt_del_{hash(tenant_id) % 10**10}",
            "type": event_type,
            "data": {
                "object": {
                    "id": f"sub_test_{tenant_id}",
                    "status": "canceled",
                }
            }
        }
    else:
        payload_data = {"id": f"evt_test_{hash(event_type) % 10**10}", "type": event_type, "data": {"object": {}}}

    payload_str = json.dumps(payload_data)

    if forge:
        stripe_signature = f"t={timestamp},v1=deadbeefdeadbeef"
    else:
        signed = f"{timestamp}.{payload_str}"
        sig = hmac.new(STRIPE_WEBHOOK_SECRET.encode(), signed.encode(), hashlib.sha256).hexdigest()
        stripe_signature = f"t={timestamp},v1={sig}"

    success, message, result = await stripe_handler.process(payload_str, stripe_signature)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"status": "simulated", "event_type": event_type, "message": message, "result": result}
