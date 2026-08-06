import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv(override=True)

CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.70"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.60"))
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ai_image")

# ─── Mismatch Guard taxonomy rules ──────────────────────────────────────────
# Maps (target_subject_keyword → rejected_candidate_keywords)
MISMATCH_RULES: Dict[str, List[str]] = {
    "fox": ["wolf", "dog", "coyote"],
    "cat": ["lion", "tiger", "cheetah", "leopard"],
    "eagle": ["hawk", "vulture", "owl"],
}

# Reverse alias resolution — semantic synonyms map to canonical subjects
SUBJECT_ALIASES: Dict[str, str] = {
    "red fox": "fox", "vulpes vulpes": "fox", "wild fox": "fox",
    "grey wolf": "wolf", "gray wolf": "wolf",
    "golden retriever": "dog", "labrador": "dog",
    "kitten": "cat", "kitty": "cat",
}

# Seed images disabled per user request
SEED_IMAGES = []
