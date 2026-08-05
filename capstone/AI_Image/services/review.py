import uuid
from typing import List, Dict, Any, Optional

from capstone.AI_Image.core.database import get_db_pool

class ReviewService:
    async def submit_review(
        self,
        image_id: str,
        post_id: str,
        approved: bool,
        reject_reason: Optional[str] = None,
        reviewer: str = "human_editor",
    ) -> Dict[str, Any]:
        review_id = f"rev_{uuid.uuid4().hex[:8]}"
        
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO reviews (review_id, image_id, post_id, approved, reject_reason, reviewer)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, review_id, image_id, post_id, approved, reject_reason, reviewer)
        
        return {
            "status": "success",
            "review_id": review_id,
            "approved": approved,
            "image_id": image_id,
        }

    async def get_reviews(self, image_id: Optional[str] = None) -> List[Dict]:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            if image_id:
                rows = await conn.fetch("SELECT * FROM reviews WHERE image_id=$1 ORDER BY created_at DESC", image_id)
            else:
                rows = await conn.fetch("SELECT * FROM reviews ORDER BY created_at DESC")
                
        return [dict(row) for row in rows]

    async def get_top1_precision(self) -> Dict[str, Any]:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT approved FROM reviews")
            
        if not rows:
            return {"total_reviews": 0, "precision_percent": "0.0%"}
            
        approvals = sum(1 for r in rows if r["approved"])
        precision = (approvals / len(rows)) * 100
        return {
            "total_reviews": len(rows),
            "precision_percent": f"{precision:.1f}%",
        }
