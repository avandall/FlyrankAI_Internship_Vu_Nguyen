import uuid
from typing import Optional, Dict, List

from capstone.Usage_metering.core.database import get_db

class TenantService:
    def create_tenant(self, name: str, email: Optional[str] = None,
                      plan: str = "free", tenant_id: Optional[str] = None) -> Dict:
        tid = tenant_id or f"t_{uuid.uuid4().hex[:8]}"
        with get_db() as conn:
            conn.execute("""
                INSERT OR IGNORE INTO tenants (tenant_id, name, email, plan)
                VALUES (?,?,?,?)
            """, (tid, name, email, plan))
            conn.commit()
            row = conn.execute("SELECT * FROM tenants WHERE tenant_id=?", (tid,)).fetchone()
        return dict(row)

    def get_tenant(self, tenant_id: str) -> Optional[Dict]:
        with get_db() as conn:
            row = conn.execute("SELECT * FROM tenants WHERE tenant_id=?", (tenant_id,)).fetchone()
        return dict(row) if row else None

    def update_plan(self, tenant_id: str, plan: str, stripe_sub_id: Optional[str] = None,
                    status: str = "active") -> bool:
        with get_db() as conn:
            conn.execute("""
                UPDATE tenants SET plan=?, subscription_status=?,
                    stripe_subscription_id=COALESCE(?, stripe_subscription_id)
                WHERE tenant_id=?
            """, (plan, status, stripe_sub_id, tenant_id))
            conn.commit()
        return True

    def get_all(self) -> List[Dict]:
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM tenants ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]
