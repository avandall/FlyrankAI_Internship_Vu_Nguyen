import re
import math
from typing import List, Dict, Any
from pathlib import Path

VISION_CONFIDENCE_BASE = 0.92

def _tokenize(text: str) -> List[str]:
    return re.findall(r"\b\w+\b", text.lower())


def compute_embedding(text: str, dim: int = 64) -> List[float]:
    """
    Deterministic text embedding using character-level n-gram hashing
    into a fixed-dim space. This is a lightweight local embedding that
    captures lexical similarity without requiring external ML models.
    For production: replace with Gemini embedding API or sentence-transformers.
    """
    tokens = _tokenize(text)
    vec = [0.0] * dim
    for token in tokens:
        for i, ch in enumerate(token):
            idx = (hash(token + str(i)) % dim + dim) % dim
            vec[idx] += 1.0
    # L2 normalize
    mag = math.sqrt(sum(v**2 for v in vec)) or 1.0
    return [round(v / mag, 6) for v in vec]


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Cosine similarity between two embedding vectors."""
    if len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    m1 = math.sqrt(sum(a**2 for a in v1)) or 1.0
    m2 = math.sqrt(sum(b**2 for b in v2)) or 1.0
    return round(dot / (m1 * m2), 4)

def call_vision_ai(filename: str, file_bytes: bytes) -> Dict[str, Any]:
    """
    Vision AI analysis pipeline.
    
    ARCHITECTURE NOTE:
    In production, this calls Gemini Flash API (free via Google AI Studio):
        import google.generativeai as genai
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([prompt, image_part])
    
    For this demo, we use filename-heuristic analysis to produce structured
    metadata that demonstrates the full pipeline without requiring API keys.
    Cost tracking is simulated at ~$0.000265 per 1000px2 input image.
    """
    base_name = Path(filename).stem.lower()
    
    # Heuristic classification from filename (production = real Vision model)
    subject_map = {
        "fox": ("fox", "animal", ["wildlife", "fox", "mammal", "forest"], "A wild fox in its natural habitat"),
        "wolf": ("wolf", "animal", ["wildlife", "wolf", "predator", "pack"], "A grey wolf standing alert in the woods"),
        "dog": ("dog", "animal", ["pet", "canine", "domesticated"], "A friendly domesticated dog"),
        "cat": ("cat", "animal", ["pet", "feline", "domestic"], "A domestic cat resting comfortably"),
        "landscape": ("landscape", "nature", ["scenery", "outdoor", "panorama"], "A sweeping natural landscape"),
        "city": ("cityscape", "urban", ["buildings", "city", "architecture"], "Urban cityscape at golden hour"),
        "mountain": ("mountain", "nature", ["mountain", "peak", "elevation", "snow"], "A mountain peak with snow cap"),
        "ocean": ("ocean", "nature", ["ocean", "waves", "coast", "sea"], "Ocean waves breaking on the shore"),
        "flower": ("flower", "nature", ["flora", "blossom", "petal", "color"], "A vibrant flower in full bloom"),
    }
    
    for key, (subject, category, attributes, caption) in subject_map.items():
        if key in base_name:
            confidence = round(VISION_CONFIDENCE_BASE - hash(filename) % 8 / 100, 3)
            ai_cost_micro_usd = 265  # $0.000265 simulated per call
            return {
                "subject": subject, "category": category,
                "attributes": attributes, "caption": caption,
                "confidence_score": max(0.4, confidence),
                "ai_cost_micro_usd": ai_cost_micro_usd,
                "model_used": "gemini-1.5-flash (simulated)",
            }
    
    # Unknown/low confidence
    return {
        "subject": "unknown", "category": "unknown",
        "attributes": ["unclear"], "caption": f"Image content unclear: {filename}",
        "confidence_score": 0.42,
        "ai_cost_micro_usd": 265,
        "model_used": "gemini-1.5-flash (simulated)",
    }

