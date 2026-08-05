from fastapi import APIRouter, Depends, Query
from capstone.Embeddeable_widget.services.submission import SubmissionService
from capstone.Embeddeable_widget.core.dependencies import require_tenant

router = APIRouter(prefix="/api", tags=["Leads Dashboard"])
submission_svc = SubmissionService()

@router.get("/leads")
async def get_leads(tenant: dict = Depends(require_tenant), limit: int = Query(50)):
    leads = submission_svc.get_for_tenant(tenant["tenant_id"], limit)
    return {"tenant_id": tenant["tenant_id"], "count": len(leads), "leads": leads}

@router.get("/stats")
async def get_stats(tenant: dict = Depends(require_tenant)):
    return submission_svc.get_stats(tenant["tenant_id"])
