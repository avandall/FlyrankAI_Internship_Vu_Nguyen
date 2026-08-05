import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
"""
Usage Metering & Billing Engine — Test Suite
Tests: integer micro-cent cost calculation, idempotent ingestion,
quota boundary 429/402 enforcement, Stripe webhook signature verification, invoice snapshot.
Run: python3 -m pytest capstone/Usage_metering/tests/test_usage_metering.py -v
"""
import sys, os, json, time, hmac, hashlib
from pathlib import Path
import pytest

os.environ['BILLING_TEST_DB'] = str(Path(__file__).parent / 'test_billing.db')

from capstone.Usage_metering.core.database import init_db
from capstone.Usage_metering.services.tenant import TenantService
from capstone.Usage_metering.services.cost import CostCalculator
from capstone.Usage_metering.services.quota import QuotaService
from capstone.Usage_metering.services.stripe import StripeWebhookHandler
from capstone.Usage_metering.core.config import STRIPE_WEBHOOK_SECRET
from capstone.Usage_metering.core.exceptions import QuotaExceededError, PaymentRequiredError

@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    import capstone.Usage_metering.core.database as db
    monkeypatch.setattr(db, 'DB_PATH', tmp_path / "test_billing.db")
    init_db()
    yield

@pytest.fixture
def tenant_svc():
    return TenantService()

@pytest.fixture
def cost_calc():
    return CostCalculator()

@pytest.fixture
def quota_svc():
    return QuotaService()

@pytest.fixture
def stripe_handler():
    return StripeWebhookHandler()


class TestCostCalculator:
    def test_integer_micro_cents_cost_calculation(self, cost_calc):
        cost_in = cost_calc.calculate_ai_cost("input", 10_000)
        cost_cached = cost_calc.calculate_ai_cost("cached_input", 10_000)
        cost_out = cost_calc.calculate_ai_cost("output", 2_500)
        
        assert isinstance(cost_in, int), "Cost must be an integer (micro-cents)"
        assert cost_in == 7_500_000
        assert cost_cached == 3_750_000  # 50% discount
        assert cost_out == 7_500_000

    def test_display_formatting(self, cost_calc):
        disp = cost_calc.micro_cents_to_display(2900_0000)  # $29.00
        assert disp == "$29.00"
        
        disp_zero = cost_calc.micro_cents_to_display(0)
        assert disp_zero == "$0.00"


class TestIdempotency:
    def test_duplicate_key_returns_existing_event_without_double_counting(
        self, tenant_svc, quota_svc
    ):
        tenant_svc.create_tenant("Acme Corp", "a@acme.com", "free", "t_acme")
        key = "idem_event_12345"

        # First ingest succeeds
        res1 = quota_svc.check_and_consume("t_acme", "api_call", 1, key)
        assert res1["idempotent"] is False

        # Second ingest with same key returns existing event, idempotent=True
        res2 = quota_svc.check_and_consume("t_acme", "api_call", 1, key)
        assert res2["idempotent"] is True

        # Check usage count is still 1 (not 2)
        usage = quota_svc.get_usage_summary("t_acme")
        assert usage["api_calls"]["used"] == 1, "Duplicate key must not increase usage counter"


class TestQuotaEnforcement:
    def test_quota_exceeded_raises_429(self, tenant_svc, quota_svc):
        tenant_svc.create_tenant("Free User", "f@test.com", "free", "t_free")
        
        # FREE plan quota: 1000 API calls
        quota_svc.check_and_consume("t_free", "api_call", 1000, "k_batch1")
        
        # 1001st call breaches quota → raises QuotaExceededError (429)
        with pytest.raises(QuotaExceededError) as exc_info:
            quota_svc.check_and_consume("t_free", "api_call", 1, "k_breach")
        
        assert "quota exceeded" in str(exc_info.value).lower()

    def test_canceled_subscription_raises_402(self, tenant_svc, quota_svc):
        tenant_svc.create_tenant("Canceled User", "c@test.com", "pro", "t_canc")
        tenant_svc.update_plan("t_canc", "free", status="canceled")
        
        with pytest.raises(PaymentRequiredError) as exc_info:
            quota_svc.check_and_consume("t_canc", "api_call", 1, "k_canc")
        
        assert "canceled" in str(exc_info.value).lower()


class TestStripeWebhooks:
    def test_valid_stripe_signature_accepted(self, tenant_svc, stripe_handler):
        tenant_svc.create_tenant("Stripe User", "s@test.com", "free", "t_stripe")
        
        payload = json.dumps({
            "id": "evt_test_1001",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer": "cus_123",
                    "subscription": "sub_456",
                    "metadata": {"tenant_id": "t_stripe"},
                }
            }
        })
        
        ts = str(int(time.time()))
        sig = hmac.new(
            STRIPE_WEBHOOK_SECRET.encode(),
            f"{ts}.{payload}".encode(),
            hashlib.sha256
        ).hexdigest()
        sig_header = f"t={ts},v1={sig}"
        
        ok, msg, res = stripe_handler.process(payload, sig_header)
        assert ok is True, f"Stripe webhook rejected: {msg}"
        assert res.get("action") == "upgraded"
        
        tenant = tenant_svc.get_tenant("t_stripe")
        assert tenant["plan"] == "pro"

    def test_forged_stripe_signature_rejected(self, stripe_handler):
        payload = json.dumps({"id": "evt_hack", "type": "checkout.session.completed"})
        bad_sig = "t=12345,v1=deadbeefdeadbeef"
        
        ok, msg, _ = stripe_handler.process(payload, bad_sig)
        assert ok is False, "Forged Stripe webhook must be rejected"

    def test_duplicate_stripe_event_deduplicated(self, tenant_svc, stripe_handler):
        tenant_svc.create_tenant("Dup User", "d@test.com", "free", "t_dup")
        
        payload = json.dumps({
            "id": "evt_dedup_99",
            "type": "customer.subscription.deleted",
            "data": {"object": {"id": "sub_test"}}
        })
        
        ts = str(int(time.time()))
        sig = hmac.new(
            STRIPE_WEBHOOK_SECRET.encode(),
            f"{ts}.{payload}".encode(),
            hashlib.sha256
        ).hexdigest()
        sig_header = f"t={ts},v1={sig}"
        
        ok1, _, _ = stripe_handler.process(payload, sig_header)
        ok2, msg2, _ = stripe_handler.process(payload, sig_header)
        
        assert ok1 is True
        assert ok2 is True
        assert "duplicate" in msg2.lower() or "already" in msg2.lower()


class TestInvoiceSnapshot:
    def test_monthly_invoice_generated(self, tenant_svc, quota_svc, cost_calc):
        tenant_svc.create_tenant("Invoice User", "inv@test.com", "pro", "t_inv")
        quota_svc.check_and_consume("t_inv", "ai_tokens", 10_000, "k1", token_type="input")
        quota_svc.check_and_consume("t_inv", "ai_tokens", 5_000, "k2", token_type="output")
        
        inv = cost_calc.monthly_invoice("t_inv")
        assert inv["tenant_id"] == "t_inv"
        assert inv["total_micro_cents"] > 0
        assert "$" in inv["total_display"]
