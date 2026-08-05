import secrets
from typing import Optional, Dict

from capstone.Embeddeable_widget.core.database import get_db_pool

class TenantService:
    async def create_tenant(self, name: str, email: str, force_id: Optional[str] = None) -> Dict:
        tenant_id = force_id or f"t_{secrets.token_hex(8)}"
        api_key = f"sk_{secrets.token_hex(16)}"
        
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO tenants (tenant_id, name, email, api_key)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (email) DO NOTHING
            """, tenant_id, name, email, api_key)
            
            # Fetch to get actual record (if it already existed)
            row = await conn.fetchrow("SELECT * FROM tenants WHERE email=$1", email)
            
        return dict(row)

    async def get_tenant_by_api_key(self, api_key: str) -> Optional[Dict]:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM tenants WHERE api_key=$1", api_key)
        return dict(row) if row else None
