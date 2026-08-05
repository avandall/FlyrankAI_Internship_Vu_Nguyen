from fastapi import APIRouter, HTTPException
from capstone.Usage_metering.services.tenant import TenantService

router = APIRouter(prefix="/api/tenants", tags=["Tenants"])
tenant_svc = TenantService()

@router.get("", summary="List all tenants")
async def list_tenants():
    return {"tenants": await tenant_svc.get_all()}

@router.post("", status_code=201, summary="Create tenant")
async def create_tenant(body: dict):
    name = body.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=422, detail="name required")
    tenant = await tenant_svc.create_tenant(name, body.get("email"), body.get("plan", "free"))
    return {"tenant": tenant}

@router.get("/{tenant_id}", summary="Get tenant")
async def get_tenant(tenant_id: str):
    tenant = await tenant_svc.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant
