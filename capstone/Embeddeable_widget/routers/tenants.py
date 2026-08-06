from fastapi import APIRouter, Depends, HTTPException
from capstone.Embeddeable_widget.services.tenant import TenantService
from capstone.Embeddeable_widget.core.dependencies import require_tenant
from capstone.Embeddeable_widget.core.config import WIDGET_API_KEY

router = APIRouter(prefix="/api/tenants", tags=["Tenants"])
tenant_svc = TenantService()

@router.get("/demo-key")
async def get_demo_key():
    """Public helper endpoint returning seeded demo API key for interactive UI testing."""
    tenant = await tenant_svc.get_tenant_by_id("t_demo")
    key = tenant.get("api_key") if tenant else WIDGET_API_KEY
    return {"api_key": key, "tenant_id": "t_demo"}

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
