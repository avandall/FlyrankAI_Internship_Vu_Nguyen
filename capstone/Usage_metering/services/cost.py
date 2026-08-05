from typing import Dict
from capstone.Usage_metering.core.config import TOKEN_PRICE_CONFIG
from capstone.Usage_metering.core.database import get_db

class CostCalculator:
    """
    Calculates cost in integer micro-cents (1 micro-cent = $0.00000001).
    Uses integer arithmetic only — no floats allowed per spec.
    """

    def calculate_ai_cost(self, token_type: str, quantity: int) -> int:
        """Returns cost in micro-cents (integer)."""
        price_per_token = TOKEN_PRICE_CONFIG.get(token_type, TOKEN_PRICE_CONFIG["input"])
        return price_per_token * quantity  # Pure integer multiplication

    def calculate_api_call_cost(self, quantity: int) -> int:
        """API call cost: flat $0.0001 per call = 1,000 micro-cents."""
        return 1_000 * quantity

    def micro_cents_to_display(self, micro_cents: int) -> str:
        """Convert micro-cents to human-readable USD string ($1 = 1,000,000 micro-cents)."""
        cents = micro_cents // 10_000
        dollars = cents // 100
        remaining_cents = cents % 100
        return f"${dollars}.{remaining_cents:02d}"

    def monthly_invoice(self, tenant_id: str) -> Dict:
        """Aggregate total cost for current billing period."""
        with get_db() as conn:
            rows = conn.execute("""
                SELECT event_type, token_type, SUM(quantity) as total_qty,
                       SUM(cost_micro_cents) as total_cost
                FROM usage_events WHERE tenant_id=?
                GROUP BY event_type, token_type
            """, (tenant_id,)).fetchall()
            total = conn.execute(
                "SELECT SUM(cost_micro_cents) as total FROM usage_events WHERE tenant_id=?",
                (tenant_id,)
            ).fetchone()["total"] or 0

        breakdown = [dict(r) for r in rows]
        return {
            "tenant_id": tenant_id,
            "breakdown": breakdown,
            "total_micro_cents": total,
            "total_display": self.micro_cents_to_display(total),
        }
