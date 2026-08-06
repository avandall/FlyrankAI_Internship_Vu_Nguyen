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
        
        # Attach image_url helper
        from pathlib import Path
        static_dir = Path(__file__).parent.parent / "static"

        # Score and evaluate all candidates
        all_candidates = []
        matched_candidates = []
        rejected_candidates = []

        for row in rows:
            img = dict(row)
            if not img.get("embedding"):
                continue
            
            # handle JSONB -> list
            img_embed = img["embedding"]
            if isinstance(img_embed, str):
                img_embed = json.loads(img_embed)

            sim = cosine_similarity(post_embed, img_embed)
            filename = img["filename"]
            image_id = img["image_id"]
            
            image_url = f"/api/images/{image_id}/file"

            # Evaluate Mismatch Guard for this individual candidate
            is_valid, reason = self.guard.evaluate(
                target_subject, target_category,
                img["subject"], img["category"],
                sim, img["confidence_score"],
            )

            cand_obj = {
                "image_id": image_id,
                "filename": filename,
                "caption": img["caption"],
                "subject": img["subject"],
                "category": img["category"],
                "confidence_score": img["confidence_score"],
                "similarity_score": sim,
                "image_url": image_url,
                "is_valid_match": is_valid,
                "guard_reason": reason,
            }

            all_candidates.append(cand_obj)
            if is_valid:
                matched_candidates.append(cand_obj)
            else:
                rejected_candidates.append(cand_obj)
        
        all_candidates.sort(key=lambda c: c["similarity_score"], reverse=True)
        matched_candidates.sort(key=lambda c: c["similarity_score"], reverse=True)

        if not all_candidates:
            return {
                "status": "NO_CONFIDENT_MATCH",
                "matched_image": None,
                "matched_candidates": [],
                "all_candidates": [],
                "reject_reason": "No images with embeddings in database",
                "top_similarity": 0.0,
            }
        
        top = all_candidates[0]
        
        if top["is_valid_match"]:
            return {
                "status": "MATCHED",
                "matched_image": top,
                "matched_candidates": matched_candidates,
                "all_candidates": all_candidates,
                "reject_reason": None,
                "top_similarity": top["similarity_score"],
            }
        elif matched_candidates:
            # Top candidate failed guard (e.g. Wolf), but another valid candidate passed (e.g. Fox)
            return {
                "status": "MATCHED",
                "matched_image": matched_candidates[0],
                "matched_candidates": matched_candidates,
                "all_candidates": all_candidates,
                "reject_reason": f"Top vector match ({top['filename']}) failed Mismatch Guard ({top['guard_reason']}), but fallback match ({matched_candidates[0]['filename']}) passed.",
                "top_similarity": matched_candidates[0]["similarity_score"],
            }
        else:
            return {
                "status": "REJECTED",
                "matched_image": None,
                "matched_candidates": [],
                "all_candidates": all_candidates,
                "reject_reason": top["guard_reason"],
                "top_similarity": top["similarity_score"],
            }
