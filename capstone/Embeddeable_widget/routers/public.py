import json
from fastapi import APIRouter, HTTPException, Request
from capstone.Embeddeable_widget.services.submission import SubmissionService
from capstone.Embeddeable_widget.core.exceptions import SpamDetectedError, RateLimitError, ValidationError

router = APIRouter(prefix="/api/public", tags=["Public Submission"])
submission_svc = SubmissionService()

MAX_PAYLOAD_SIZE = 100 * 1024  # 100 KB limit

@router.post("/submit")
async def public_submit(request: Request):
    # 1. Payload size check (413 Payload Too Large)
    content_length = request.headers.get("Content-Length")
    if content_length and int(content_length) > MAX_PAYLOAD_SIZE:
        raise HTTPException(status_code=413, detail="Payload too large (max 100KB)")

    raw_body = await request.body()
    if len(raw_body) > MAX_PAYLOAD_SIZE:
        raise HTTPException(status_code=413, detail="Payload too large (max 100KB)")

    try:
        body = json.loads(raw_body.decode("utf-8")) if raw_body else {}
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid JSON payload")

    widget_id = body.get("widget_id", "")
    if not widget_id:
        raise HTTPException(status_code=422, detail="widget_id is required")

    forwarded_for = request.headers.get("X-Forwarded-For")
    source_ip = forwarded_for.split(",")[0].strip() if forwarded_for else (request.client.host if request.client else "127.0.0.1")
    source_origin = request.headers.get("Origin", "unknown")

    try:
        result = await submission_svc.submit(widget_id, body, source_ip, source_origin)
        return {"status": "success", "submission": result}
    except SpamDetectedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e), headers={"Retry-After": "60"})
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
