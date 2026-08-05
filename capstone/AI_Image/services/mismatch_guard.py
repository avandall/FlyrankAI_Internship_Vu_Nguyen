from typing import Optional, Tuple
from capstone.AI_Image.core.config import CONFIDENCE_THRESHOLD, SIMILARITY_THRESHOLD, MISMATCH_RULES, SUBJECT_ALIASES

class MismatchGuard:
    """
    Safety layer: combines Tag/Category alignment + Similarity threshold
    + Confidence score to decide if a candidate image is valid.
    """

    def _resolve_canonical(self, subject: str) -> str:
        s = subject.strip().lower()
        return SUBJECT_ALIASES.get(s, s)

    def evaluate(
        self,
        target_subject: Optional[str],
        target_category: Optional[str],
        candidate_subject: str,
        candidate_category: str,
        similarity: float,
        confidence: float,
    ) -> Tuple[bool, Optional[str]]:
        
        # 1. Explicit mismatch guard (taxonomy rules)
        if target_subject:
            target_canon = self._resolve_canonical(target_subject)
            cand_canon = self._resolve_canonical(candidate_subject)
            
            for rule_key, forbidden in MISMATCH_RULES.items():
                if rule_key in target_canon:
                    for forbidden_subj in forbidden:
                        if forbidden_subj in cand_canon:
                            return False, (
                                f"Animal category mismatch: expected {target_subject}, "
                                f"detected {candidate_subject}"
                            )
        
        # 2. Category alignment
        if target_category and target_category.lower() != candidate_category.lower():
            return False, (
                f"Category mismatch: expected '{target_category}', "
                f"detected '{candidate_category}'"
            )
        
        # 3. Similarity threshold
        if similarity < SIMILARITY_THRESHOLD:
            return False, (
                f"No confident match: similarity {similarity:.2f} below "
                f"threshold {SIMILARITY_THRESHOLD:.2f}"
            )
        
        # 4. Confidence score guard
        if confidence < CONFIDENCE_THRESHOLD:
            return False, (
                f"Image confidence {confidence:.2f} below minimum "
                f"threshold {CONFIDENCE_THRESHOLD:.2f} — flagged image excluded"
            )
        
        return True, None
