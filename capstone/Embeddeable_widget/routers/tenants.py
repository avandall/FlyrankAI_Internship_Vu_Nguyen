from fastapi import APIRouter, Depends, HTTPException
from capstone.Embeddeable_widget.services.tenant import TenantService
from capstone.Embeddeable_widget.core.dependencies import require_tenant

router = APIRouter(prefix="/api/tenants", tags=["Tenants"])
tenant_svc = TenantService()

@router.post("", status_code=201)
async def create_tenant(body: dict):
    name = body.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=422, detail="name is required")
    tenant = await tenant_svc.create_tenant(name, body.get("email"))
    return {"tenant": tenant, "message": "Save your api_key — it won't be shown again"}

@router.get("/me")
async def get_my_tenant(tenant: dict = Depends(require_tenant)):
    return {"tenant": {k: v for k, v in tenant.items() if k != "api_key"}}
