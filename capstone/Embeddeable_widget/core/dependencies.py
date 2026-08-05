from typing import Optional
from fastapi import Header, HTTPException
from capstone.Embeddeable_widget.services.tenant import TenantService

tenant_svc = TenantService()

async def require_tenant(x_api_key: Optional[str] = Header(None)) -> dict:
    if not x_api_key:
        raise HTTPException(status_code=401, detail="X-API-Key header required")
    tenant = await tenant_svc.get_tenant_by_api_key(x_api_key)
    if not tenant:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return tenant
