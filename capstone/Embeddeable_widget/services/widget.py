import uuid
import json
from datetime import datetime
from typing import Optional, List, Dict

from capstone.Embeddeable_widget.core.database import get_db
from capstone.Embeddeable_widget.core.config import RATE_LIMIT_MAX_REQUESTS

class WidgetService:
    def create_widget(self, tenant_id: str, data: Dict) -> Dict:
        widget_id = data.get("widget_id") or f"w_{uuid.uuid4().hex[:10]}"
        with get_db() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO widgets
                (widget_id, tenant_id, name, form_type, title, description,
                 button_text, allowed_domains, rate_limit_per_min, webhook_url,
                 primary_color, version)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                widget_id, tenant_id,
                data.get("name", "My Widget"),
                data.get("form_type", "contact"),
                data.get("title"),
                data.get("description"),
                data.get("button_text", "Submit"),
                json.dumps(data.get("allowed_domains", [])),
                data.get("rate_limit_per_min", RATE_LIMIT_MAX_REQUESTS),
                data.get("webhook_url"),
                data.get("primary_color", "#38BDF8"),
                1,
            ))
            conn.commit()
            row = conn.execute("SELECT * FROM widgets WHERE widget_id=?", (widget_id,)).fetchone()
        return self._format(dict(row))

    def get_widget(self, widget_id: str) -> Optional[Dict]:
        with get_db() as conn:
            row = conn.execute("SELECT * FROM widgets WHERE widget_id=?", (widget_id,)).fetchone()
        return self._format(dict(row)) if row else None

    def get_for_tenant(self, tenant_id: str) -> List[Dict]:
        with get_db() as conn:
            rows = conn.execute(
                "SELECT * FROM widgets WHERE tenant_id=? ORDER BY created_at DESC", (tenant_id,)
            ).fetchall()
        return [self._format(dict(r)) for r in rows]

    def update_widget(self, widget_id: str, tenant_id: str, data: Dict) -> Optional[Dict]:
        """Multi-tenant: only owner can update."""
        with get_db() as conn:
            row = conn.execute(
                "SELECT * FROM widgets WHERE widget_id=? AND tenant_id=?", (widget_id, tenant_id)
            ).fetchone()
            if not row:
                return None
            conn.execute("""
                UPDATE widgets SET
                    name=?, form_type=?, title=?, description=?,
                    button_text=?, allowed_domains=?, rate_limit_per_min=?,
                    webhook_url=?, primary_color=?, version=version+1, updated_at=?
                WHERE widget_id=? AND tenant_id=?
            """, (
                data.get("name", row["name"]),
                data.get("form_type", row["form_type"]),
                data.get("title", row["title"]),
                data.get("description", row["description"]),
                data.get("button_text", row["button_text"]),
                json.dumps(data.get("allowed_domains", json.loads(row["allowed_domains"]))),
                data.get("rate_limit_per_min", row["rate_limit_per_min"]),
                data.get("webhook_url", row["webhook_url"]),
                data.get("primary_color", row["primary_color"]),
                datetime.utcnow().isoformat(),
                widget_id, tenant_id,
            ))
            conn.commit()
            row = conn.execute("SELECT * FROM widgets WHERE widget_id=?", (widget_id,)).fetchone()
        return self._format(dict(row))

    def delete_widget(self, widget_id: str, tenant_id: str) -> bool:
        with get_db() as conn:
            result = conn.execute(
                "DELETE FROM widgets WHERE widget_id=? AND tenant_id=?", (widget_id, tenant_id)
            )
            conn.commit()
        return result.rowcount > 0

    def generate_embed_snippet(self, widget_id: str, base_url: str = "http://localhost:8002") -> str:
        """Returns versioned <script> embed snippet."""
        widget = self.get_widget(widget_id)
        version = widget.get("version", 1) if widget else 1
        return f'<script src="{base_url}/widget.js?id={widget_id}&v={version}" defer></script>'

    def _format(self, row: Dict) -> Dict:
        if row.get("allowed_domains") and isinstance(row["allowed_domains"], str):
            row["allowed_domains"] = json.loads(row["allowed_domains"])
        return row
