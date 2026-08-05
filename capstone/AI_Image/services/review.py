import uuid
from typing import Optional, Dict, Any, List

from capstone.AI_Image.core.database import get_db

class ReviewService:
    """Human review workflow: Approve/Reject AI suggestions with audit trail."""

    def submit_review(
        self,
        image_id: str,
        post_id: str,
        approved: bool,
        reject_reason: Optional[str] = None,
        reviewer: str = "human_editor",
    ) -> Dict[str, Any]:
        review_id = f"rev_{uuid.uuid4().hex[:8]}"
        with get_db() as conn:
            conn.execute("""
                INSERT INTO reviews (review_id, image_id, post_id, approved, reject_reason, reviewer)
                VALUES (?,?,?,?,?,?)
            """, (review_id, image_id, post_id, 1 if approved else 0, reject_reason, reviewer))
            conn.commit()
        return {
            "review_id": review_id,
            "image_id": image_id,
            "post_id": post_id,
            "approved": approved,
            "reject_reason": reject_reason,
            "reviewer": reviewer,
        }

    def get_reviews(self, image_id: Optional[str] = None) -> List[Dict]:
        with get_db() as conn:
            if image_id:
                rows = conn.execute(
                    "SELECT * FROM reviews WHERE image_id=? ORDER BY created_at DESC", (image_id,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM reviews ORDER BY created_at DESC LIMIT 50"
                ).fetchall()
        return [dict(r) for r in rows]

    def get_top1_precision(self) -> Dict[str, Any]:
        """Calculate Top-1 Precision metric on all approved reviews."""
        with get_db() as conn:
            total = conn.execute("SELECT COUNT(*) as c FROM reviews").fetchone()["c"]
            approved = conn.execute(
                "SELECT COUNT(*) as c FROM reviews WHERE approved=1"
            ).fetchone()["c"]
        precision = round(approved / total, 4) if total else 0.0
        return {
            "total_reviews": total,
            "approved": approved,
            "rejected": total - approved,
            "top1_precision": precision,
            "precision_pct": f"{precision * 100:.1f}%",
        }
