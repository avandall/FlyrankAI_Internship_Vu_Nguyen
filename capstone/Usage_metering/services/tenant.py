import uuid
from typing import Optional, Dict, List

from capstone.Usage_metering.core.database import get_db_pool

class TenantService:
    async def create_tenant(self, name: str, email: Optional[str] = None,
                      plan: str = "free", tenant_id: Optional[str] = None) -> Dict:
        tid = tenant_id or f"t_{uuid.uuid4().hex[:8]}"
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO tenants (tenant_id, name, email, plan)
                VALUES ($1,$2,$3,$4)
                ON CONFLICT (tenant_id) DO NOTHING
            """, tid, name, email, plan)
            row = await conn.fetchrow("SELECT * FROM tenants WHERE tenant_id=$1", tid)
        return dict(row) if row else {}

    async def get_tenant(self, tenant_id: str) -> Optional[Dict]:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM tenants WHERE tenant_id=$1", tenant_id)
        return dict(row) if row else None

    async def update_plan(self, tenant_id: str, plan: str, stripe_sub_id: Optional[str] = None,
                    status: str = "active") -> bool:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE tenants SET plan=$1, subscription_status=$2,
                    stripe_subscription_id=COALESCE($3, stripe_subscription_id)
                WHERE tenant_id=$4
            """, plan, status, stripe_sub_id, tenant_id)
        return True

    async def get_all(self) -> List[Dict]:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM tenants ORDER BY created_at DESC")
        return [dict(r) for r in rows]
