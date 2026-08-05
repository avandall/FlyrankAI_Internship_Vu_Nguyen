import json
import hmac
import hashlib
from fastapi import APIRouter, HTTPException, Request
from capstone.Multi_platform.services.webhook import WebhookHandler
from capstone.Multi_platform.services.fake_social import FakeSocialPlatformServer

router = APIRouter(tags=["Webhooks"])
webhook_handler = WebhookHandler()

@router.post("/webhook/social-delivery", summary="Receive webhook from Fake Social Platform")
async def receive_webhook(request: Request):
    raw_body = await request.body()
    payload_str = raw_body.decode("utf-8")
    signature = request.headers.get("X-Hub-Signature-256", "")

    valid, message = await webhook_handler.receive(payload_str, signature)

    if not valid:
        raise HTTPException(status_code=400, detail=message)

    return {"status": "ok", "message": message}

@router.post("/api/webhook/test", summary="Simulate Fake Server webhook delivery")
async def simulate_webhook(body: dict):
    post_id = body.get("post_id", "test_post_id")
    platform = body.get("platform", "instagram")
    forge_signature = body.get("forge_signature", False)

    payload = json.dumps({
        "event": "post.published",
        "post_id": post_id,
        "platform": platform,
        "status": "published",
    })

    if forge_signature:
        signature = "sha256=deadbeefdeadbeef"
    else:
        real_sig = hmac.new(
            FakeSocialPlatformServer.WEBHOOK_SECRET.encode(),
            payload.encode(), hashlib.sha256
        ).hexdigest()
        signature = real_sig

    valid, message = await webhook_handler.receive(payload, signature)
    return {
        "signature_valid": valid,
        "message": message,
        "post_id": post_id,
    }
