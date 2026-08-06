import os
from dotenv import load_dotenv

load_dotenv(override=True)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/multi_platform")
WEBHOOK_HMAC_SECRET = os.getenv("WEBHOOK_HMAC_SECRET", "whsec_multiplatform_secret_555")
IDEMPOTENCY_TTL_SECONDS = int(os.getenv("IDEMPOTENCY_TTL_SECONDS", "3600"))

PLATFORM_SPECS = {

    "instagram": {
        "width": 1080, "height": 1080, "ratio": "1:1",
        "max_caption_chars": 2200,
        "style": "visual, emoji-rich, hashtag-heavy, personal and inspiring",
    },
    "twitter": {
        "width": 1600, "height": 900, "ratio": "16:9",
        "max_caption_chars": 280,
        "style": "concise, punchy, conversational, one key hook, no hashtag spam",
    },
    "linkedin": {
        "width": 1200, "height": 628, "ratio": "1.91:1",
        "max_caption_chars": 700,
        "style": "professional, insight-driven, thoughtful tone, industry focus",
    },
}
