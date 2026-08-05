import os

# 1 micro-cent = $0.00000001. Prices are per-token in micro-cents.
# Based on Gemini Flash pricing (representative AI model)
TOKEN_PRICE_CONFIG = {
    "input": 750,           # $0.0000075 per token = 750 micro-cents
    "cached_input": 375,    # 50% discount for cached input
    "output": 3000,         # $0.00003 per token = 3000 micro-cents
    "reasoning": 3000,      # Same as output tokens
}

# ─── Default plans with quotas ───────────────────────────────────────────────
DEFAULT_PLANS = {
    "free": {
        "quota_api_calls": 1000,
        "quota_ai_tokens": 100_000,
        "monthly_price_cents": 0,
    },
    "pro": {
        "quota_api_calls": 100_000,
        "quota_ai_tokens": 10_000_000,
        "monthly_price_cents": 2900,  # $29.00
    },
    "enterprise": {
        "quota_api_calls": 10_000_000,
        "quota_ai_tokens": 1_000_000_000,
        "monthly_price_cents": 29900,  # $299.00
    },
}

# Stripe test webhook secret (in production: loaded from env, never hardcoded)
STRIPE_WEBHOOK_SECRET = os.environ.get(
    "STRIPE_WEBHOOK_SECRET", "whsec_test_fake_capstone_secret_12345"
)
