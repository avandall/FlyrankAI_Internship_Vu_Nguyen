import os
import json
import math
import httpx
import base64
from typing import List, Dict, Any
from groq import AsyncGroq
from pydantic import BaseModel, ValidationError

class VisionAIResult(BaseModel):
    subject: str
    category: str
    attributes: List[str]
    caption: str
    confidence_score: float

async def compute_embedding(text: str) -> List[float]:
    """Compute semantic embeddings using sentence-transformers (all-MiniLM-L6-v2)."""
    try:
        from sentence_transformers import SentenceTransformer
        # Cache the model in a global variable to avoid reloading it
        if not hasattr(compute_embedding, "_model"):
            compute_embedding._model = SentenceTransformer('all-MiniLM-L6-v2')
        model = compute_embedding._model
        
        # SentenceTransformer encode is synchronous, but we can run it in a thread or just run it directly 
        # since it's very fast for a single sentence.
        embedding = model.encode(text).tolist()
        return [float(x) for x in embedding]
    except ImportError:
        import logging
        logging.getLogger(__name__).error("sentence-transformers not installed, falling back to mock")
        # Fallback pseudo-embedding
        dim = 384
        import re, math
        tokens = re.findall(r"\b\w+\b", text.lower())
        vec = [0.0] * dim
        for token in tokens:
            for i, ch in enumerate(token):
                idx = (hash(token + str(i)) % dim + dim) % dim
                vec[idx] += 1.0
        mag = math.sqrt(sum(v**2 for v in vec)) or 1.0
        return [round(v / mag, 6) for v in vec]

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    m1 = math.sqrt(sum(a**2 for a in v1)) or 1.0
    m2 = math.sqrt(sum(b**2 for b in v2)) or 1.0
    return round(dot / (m1 * m2), 4)

async def call_vision_ai(filename: str, file_bytes: bytes) -> Dict[str, Any]:
    """Call Groq Llama-3.2 Vision for structured output."""
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY is missing")

    client = AsyncGroq(api_key=groq_api_key)
    
    # Encode image
    b64_img = base64.b64encode(file_bytes).decode('utf-8')
    mime_type = "image/jpeg" if filename.lower().endswith(('.jpg', '.jpeg')) else "image/png"
    if filename.lower().endswith('.webp'):
        mime_type = "image/webp"

    schema_str = """
    {
      "subject": "string (e.g. red fox)",
      "category": "string (e.g. animal, landscape)",
      "attributes": ["string", "string"],
      "caption": "string describing the image",
      "confidence_score": float (0.0 to 1.0)
    }
    """

    prompt = f"Analyze this image and return a JSON object with this exact schema: {schema_str}. Do not include markdown formatting or other text, just raw JSON."

    completion = await client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "llama-3.2-11b-vision-preview"),
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64_img}"}},
                ],
            }
        ],
        temperature=0.1,
    )

    response_text = completion.choices[0].message.content
    try:
        # Sometimes models wrap json in ```json
        if response_text.startswith("```json"):
            response_text = response_text[7:-3]
        elif response_text.startswith("```"):
            response_text = response_text[3:-3]
            
        data = json.loads(response_text.strip())
        validated = VisionAIResult(**data)
        
        # Calculate mock cost since Groq free tier doesn't easily expose exact billing
        ai_cost = 265  # $0.000265
        
        return {
            **validated.model_dump(),
            "ai_cost_micro_usd": ai_cost,
            "model_used": completion.model,
        }
    except (json.JSONDecodeError, ValidationError) as e:
        raise ValueError(f"Vision model returned invalid schema: {e}")
