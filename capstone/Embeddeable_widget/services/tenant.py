import secrets
from typing import Optional, Dict

from capstone.Embeddeable_widget.core.database import get_db_pool
from capstone.Embeddeable_widget.schemas import format_db_row
from capstone.Embeddeable_widget.core.config import WIDGET_API_KEY

class TenantService:
    async def create_tenant(
        self,
        name: str,
        email: str,
        force_id: Optional[str] = None,
        force_api_key: Optional[str] = None,
    ) -> Dict:
        tenant_id = force_id or f"t_{secrets.token_hex(8)}"
        api_key = force_api_key or f"sk_{secrets.token_hex(16)}"
        
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO tenants (tenant_id, name, email, api_key)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name
            """, tenant_id, name, email, api_key)
            
            row = await conn.fetchrow("SELECT * FROM tenants WHERE email=$1", email)
            
        return format_db_row(dict(row))

    async def get_tenant_by_api_key(self, api_key: str) -> Optional[Dict]:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM tenants WHERE api_key=$1", api_key)
        return format_db_row(dict(row)) if row else None

    async def get_tenant_by_id(self, tenant_id: str) -> Optional[Dict]:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM tenants WHERE tenant_id=$1", tenant_id)
        return format_db_row(dict(row)) if row else None
