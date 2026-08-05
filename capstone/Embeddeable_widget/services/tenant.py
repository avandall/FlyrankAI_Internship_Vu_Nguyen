import uuid
from typing import Optional, List, Dict

from capstone.Embeddeable_widget.core.database import get_db

class TenantService:
    def create_tenant(self, name: str, email: Optional[str] = None, tenant_id: Optional[str] = None) -> Dict:
        tid = tenant_id or f"t_{uuid.uuid4().hex[:8]}"
        api_key = f"wk_{uuid.uuid4().hex}"
        with get_db() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO tenants (tenant_id, name, api_key, email) VALUES (?,?,?,?)",
                (tid, name, api_key, email)
            )
            conn.commit()
            row = conn.execute("SELECT * FROM tenants WHERE tenant_id=?", (tid,)).fetchone()
        return dict(row)

    def get_by_api_key(self, api_key: str) -> Optional[Dict]:
        with get_db() as conn:
            row = conn.execute("SELECT * FROM tenants WHERE api_key=?", (api_key,)).fetchone()
        return dict(row) if row else None

    def get_all(self) -> List[Dict]:
        with get_db() as conn:
            rows = conn.execute("SELECT tenant_id, name, email, created_at FROM tenants").fetchall()
        return [dict(r) for r in rows]
