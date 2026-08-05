import json
from typing import Optional, Dict, Any

from capstone.AI_Image.core.database import get_db_pool
from capstone.AI_Image.utils import compute_embedding, cosine_similarity
from capstone.AI_Image.services.mismatch_guard import MismatchGuard

class ContentMatchingEngine:
    """
    Matches blog post to best image using:
    1. Semantic vector embedding similarity (cosine distance calculated in python)
    2. Mismatch Guard safety checks
    """

    def __init__(self):
        self.guard = MismatchGuard()

    async def match_post(
        self,
        post_id: str,
        title: str,
        text: str,
        target_subject: Optional[str] = None,
        target_category: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Generate embedding for post content
        post_embed = await compute_embedding(f"{title} {text}")
        
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            # Fetch all non-flagged images. Since we don't have pgvector, we fetch embeddings and compute locally.
            # In a massive DB we'd use pgvector, but PDF states "in-DB arrays fine at this scale".
            rows = await conn.fetch("SELECT * FROM images WHERE is_flagged=0")
        
        if not rows:
            return {
                "status": "NO_CONFIDENT_MATCH",
                "matched_image": None,
                "all_candidates": [],
                "reject_reason": "No valid non-flagged images in database",
                "top_similarity": 0.0,
            }
        
        # Score all candidates
        candidates = []
        for row in rows:
            img = dict(row)
            if not img.get("embedding"):
                continue
            
            # handle JSONB -> list
            img_embed = img["embedding"]
            if isinstance(img_embed, str):
                img_embed = json.loads(img_embed)

            sim = cosine_similarity(post_embed, img_embed)
            candidates.append({
                "image_id": img["image_id"],
                "filename": img["filename"],
                "caption": img["caption"],
                "subject": img["subject"],
                "category": img["category"],
                "confidence_score": img["confidence_score"],
                "similarity_score": sim,
            })
        
        candidates.sort(key=lambda c: c["similarity_score"], reverse=True)
        
        if not candidates:
            return {
                "status": "NO_CONFIDENT_MATCH",
                "matched_image": None,
                "all_candidates": [],
                "reject_reason": "No images with embeddings in database",
                "top_similarity": 0.0,
            }
        
        top = candidates[0]
        
        # Mismatch Guard evaluation
        is_valid, reason = self.guard.evaluate(
            target_subject, target_category,
            top["subject"], top["category"],
            top["similarity_score"], top["confidence_score"],
        )
        
        if not is_valid:
            return {
                "status": "REJECTED",
                "matched_image": None,
                "all_candidates": candidates[:5],
                "reject_reason": reason,
                "top_similarity": top["similarity_score"],
            }
        
        return {
            "status": "MATCHED",
            "matched_image": top,
            "all_candidates": candidates[:5],
            "reject_reason": None,
            "top_similarity": top["similarity_score"],
        }
