import os
from dotenv import load_dotenv

load_dotenv()

RATE_LIMIT_WINDOW_SECS = int(os.getenv("RATE_LIMIT_WINDOW_SECS", "60"))
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "5"))
WIDGET_API_KEY = os.getenv("WIDGET_API_KEY", "demo_secret_key_123")
WEBHOOK_SECRET_KEY = os.getenv("WEBHOOK_SECRET_KEY", "whsec_widget_secret_999")
ALLOWED_DOMAINS = os.getenv("ALLOWED_DOMAINS", "localhost,127.0.0.1,flyrank.ai").split(",")

