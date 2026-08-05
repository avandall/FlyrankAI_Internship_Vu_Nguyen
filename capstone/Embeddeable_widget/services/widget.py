import secrets
import json
from datetime import datetime
from typing import Optional, Dict

from capstone.Embeddeable_widget.core.database import get_db_pool

class WidgetService:
    async def create_widget(self, tenant_id: str, data: Dict) -> Dict:
        widget_id = data.get("widget_id") or f"w_{secrets.token_hex(5)}"
        allowed_domains = json.dumps(data.get("allowed_domains", []))
        
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO widgets (
                    widget_id, tenant_id, name, form_type, title, description,
                    button_text, allowed_domains, rate_limit_per_min, webhook_url, primary_color, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, CURRENT_TIMESTAMP)
                ON CONFLICT (widget_id) DO NOTHING
            """,
                widget_id, tenant_id, data.get("name", "My Widget"), data.get("form_type", "contact"),
                data.get("title"), data.get("description"), data.get("button_text", "Submit"),
                allowed_domains, data.get("rate_limit_per_min", 10),
                data.get("webhook_url"), data.get("primary_color", "#38BDF8")
            )
            
            row = await conn.fetchrow("SELECT * FROM widgets WHERE widget_id=$1", widget_id)
        
        return self._format(dict(row)) if row else data

    async def get_widget(self, widget_id: str) -> Optional[Dict]:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM widgets WHERE widget_id=$1", widget_id)
            
        if not row:
            return None
        return self._format(dict(row))

    async def get_for_tenant(self, tenant_id: str) -> list[Dict]:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM widgets WHERE tenant_id=$1 ORDER BY created_at DESC", tenant_id)
            
        return [self._format(dict(r)) for r in rows]

    async def update_widget(self, widget_id: str, tenant_id: str, data: Dict) -> Optional[Dict]:
        """Multi-tenant: only owner can update."""
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM widgets WHERE widget_id=$1 AND tenant_id=$2", widget_id, tenant_id)
            if not row:
                return None
            
            allowed_domains = json.dumps(data.get("allowed_domains")) if "allowed_domains" in data else row["allowed_domains"]
            
            await conn.execute("""
                UPDATE widgets SET
                    name=$1, form_type=$2, title=$3, description=$4,
                    button_text=$5, allowed_domains=$6, rate_limit_per_min=$7,
                    webhook_url=$8, primary_color=$9
                WHERE widget_id=$10 AND tenant_id=$11
            """,
                data.get("name", row["name"]),
                data.get("form_type", row["form_type"]),
                data.get("title", row["title"]),
                data.get("description", row["description"]),
                data.get("button_text", row["button_text"]),
                allowed_domains,
                data.get("rate_limit_per_min", row["rate_limit_per_min"]),
                data.get("webhook_url", row["webhook_url"]),
                data.get("primary_color", row["primary_color"]),
                widget_id, tenant_id,
            )
            updated_row = await conn.fetchrow("SELECT * FROM widgets WHERE widget_id=$1", widget_id)
        
        return self._format(dict(updated_row))

    async def delete_widget(self, widget_id: str, tenant_id: str) -> bool:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            status = await conn.execute("DELETE FROM widgets WHERE widget_id=$1 AND tenant_id=$2", widget_id, tenant_id)
            return status != "DELETE 0"

    async def generate_embed_snippet(self, widget_id: str, base_url: str = "http://localhost:8002") -> str:
        """Returns versioned <script> embed snippet."""
        widget = await self.get_widget(widget_id)
        # Using a simple hash of updated_at or 1 if missing for version
        version = 1
        if widget and widget.get("updated_at"):
             version = hash(widget["updated_at"]) % 10000
        return f'<script src="{base_url}/widget.js?id={widget_id}&v={version}" defer></script>'

    def _format(self, row: Dict) -> Dict:
        if row.get("allowed_domains") and isinstance(row["allowed_domains"], str):
            row["allowed_domains"] = json.loads(row["allowed_domains"])
        return row
