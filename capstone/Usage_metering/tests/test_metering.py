"""
Usage Metering & Billing Engine — Test Suite
Tests: idempotency (no double-counting), quota 429, payment 402,
AI token cost calculation (integer math), Stripe webhook HMAC,
boundary conditions, multi-tenant isolation.
Run: python3 -m pytest capstone/Usage_metering/tests/test_metering.py -v
"""
import sys, os, json, time, hmac, hashlib, uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

import pytest
from pathlib import Path


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    import capstone.Usage_metering.core.database as db
    monkeypatch.setattr(db, 'DB_PATH', tmp_path / "test_billing.db")
    db.init_db()
    yield


@pytest.fixture
def tenants():
    from capstone.Usage_metering.services.tenant import TenantService
    return TenantService()


@pytest.fixture
def quota():
    from capstone.Usage_metering.services.quota import QuotaService
    return QuotaService()


@pytest.fixture
def calc():
    from capstone.Usage_metering.services.cost import CostCalculator
    return CostCalculator()


@pytest.fixture
def stripe():
    from capstone.Usage_metering.services.stripe import StripeWebhookHandler
    return StripeWebhookHandler()


# ═══════════════════════════════════════════════════════════════════════════
# 1. COST CALCULATION — Integer arithmetic, correct token pricing
# ═══════════════════════════════════════════════════════════════════════════

class TestCostCalculation:
    def test_output_token_cost_is_integer(self, calc):
        cost = calc.calculate_ai_cost("output", 1000)
        assert isinstance(cost, int), f"Cost must be integer, got {type(cost)}"

    def test_input_token_price(self, calc):
        # 1000 input tokens at 750 micro-cents each = 750,000 micro-cents
        cost = calc.calculate_ai_cost("input", 1000)
        assert cost == 750_000, f"Expected 750000, got {cost}"

    def test_cached_input_is_50_percent_discount(self, calc):
        regular = calc.calculate_ai_cost("input", 1000)
        cached = calc.calculate_ai_cost("cached_input", 1000)
        assert cached == regular // 2, f"Cached should be 50% of regular: {cached} vs {regular // 2}"

    def test_output_token_price(self, calc):
        # 1000 output tokens at 3000 micro-cents each = 3,000,000 micro-cents
        cost = calc.calculate_ai_cost("output", 1000)
        assert cost == 3_000_000, f"Expected 3000000, got {cost}"

    def test_reasoning_equals_output(self, calc):
        output_cost = calc.calculate_ai_cost("output", 500)
        reasoning_cost = calc.calculate_ai_cost("reasoning", 500)
        assert output_cost == reasoning_cost, "Reasoning tokens priced same as output"

    def test_no_floats_in_calculation(self, calc):
        """Verify all internal calculations avoid floats."""
        cost = calc.calculate_ai_cost("output", 777)
        assert isinstance(cost, int)
        # 777 * 3000 = 2,331,000 (no rounding needed)
        assert cost == 777 * 3000

    def test_api_call_cost(self, calc):
        # 1000 API calls at 1000 micro-cents each = 1,000,000 micro-cents = $0.01
        cost = calc.calculate_api_call_cost(1000)
        assert cost == 1_000_000

    def test_display_formatting(self, calc):
        # $1.00 = 1,000,000 micro-cents
        display = calc.micro_cents_to_display(1_000_000)
        assert display == "$1.00", f"Expected $1.00, got {display}"


# ═══════════════════════════════════════════════════════════════════════════
# 2. IDEMPOTENCY — No double counting
# ═══════════════════════════════════════════════════════════════════════════

class TestIdempotency:
    @pytest.fixture(autouse=True)
    def tenant(self, tenants):
        self.t = tenants.create_tenant("Idem Corp", plan="pro")

    def test_same_key_returns_existing_event(self, quota):
        key = f"idem_{uuid.uuid4().hex}"
        evt1 = quota.check_and_consume(self.t["tenant_id"], "api_call", 1, key)
        evt2 = quota.check_and_consume(self.t["tenant_id"], "api_call", 1, key)
        assert evt1["event_id"] == evt2["event_id"]
        assert evt2.get("idempotent") is True

    def test_duplicate_does_not_double_count_usage(self, quota):
        key = f"idem_{uuid.uuid4().hex}"
        quota.check_and_consume(self.t["tenant_id"], "api_call", 100, key)
        quota.check_and_consume(self.t["tenant_id"], "api_call", 100, key)  # Duplicate
        summary = quota.get_usage_summary(self.t["tenant_id"])
        assert summary["api_calls"]["used"] == 100, \
            f"Usage should be 100, not 200. Got {summary['api_calls']['used']}"

    def test_different_keys_both_recorded(self, quota):
        quota.check_and_consume(self.t["tenant_id"], "api_call", 50, "key_a")
        quota.check_and_consume(self.t["tenant_id"], "api_call", 50, "key_b")
        summary = quota.get_usage_summary(self.t["tenant_id"])
        assert summary["api_calls"]["used"] == 100, \
            f"Both events should be recorded. Got {summary['api_calls']['used']}"


# ═══════════════════════════════════════════════════════════════════════════
# 3. QUOTA ENFORCEMENT — 429 boundary tests
# ═══════════════════════════════════════════════════════════════════════════

class TestQuotaEnforcement:
    def test_quota_check_before_limit_passes(self, quota, tenants):
        """Request 999 of 1000 — should pass."""
        t = tenants.create_tenant("Near Limit Corp", plan="free")
        evt = quota.check_and_consume(t["tenant_id"], "api_call", 999, "key_999")
        assert evt["event_id"] is not None

    def test_quota_exceeded_raises_429_error(self, quota, tenants):
        """Request 1001 of 1000 — should raise QuotaExceededError."""
        from capstone.Usage_metering.core.exceptions import QuotaExceededError
        t = tenants.create_tenant("Over Limit Corp", plan="free")
        with pytest.raises(QuotaExceededError) as exc_info:
            quota.check_and_consume(t["tenant_id"], "api_call", 1001, "key_over")
        assert "quota exceeded" in str(exc_info.value).lower() or "1001" in str(exc_info.value)

    def test_boundary_1000th_request_passes(self, quota, tenants):
        """Exactly request 1000 — boundary case, must PASS."""
        t = tenants.create_tenant("Boundary Corp", plan="free")
        # First consume 999
        quota.check_and_consume(t["tenant_id"], "api_call", 999, "key_pre")
        # 1000th request must succeed
        evt = quota.check_and_consume(t["tenant_id"], "api_call", 1, "key_1000")
        assert evt is not None, "Exactly hitting quota limit should succeed"

    def test_1001th_request_fails(self, quota, tenants):
        """Request 1001 after using 1000 — must FAIL with 429."""
        from capstone.Usage_metering.core.exceptions import QuotaExceededError
        t = tenants.create_tenant("Over Boundary Corp", plan="free")
        quota.check_and_consume(t["tenant_id"], "api_call", 1000, "key_all")
        with pytest.raises(QuotaExceededError):
            quota.check_and_consume(t["tenant_id"], "api_call", 1, "key_1001")

    def test_pro_plan_higher_quota(self, quota, tenants):
        """Pro plan quota is 100x higher than free."""
        t = tenants.create_tenant("Pro Corp", plan="pro")
        # Free plan limit is 1000; pro is 100,000
        evt = quota.check_and_consume(t["tenant_id"], "api_call", 50000, "key_pro")
        assert evt is not None, "Pro tenant should handle 50k API calls"


# ═══════════════════════════════════════════════════════════════════════════
# 4. HTTP 402 — Inactive subscription
# ═══════════════════════════════════════════════════════════════════════════

class TestPaymentRequired:
    def test_canceled_subscription_raises_402(self, quota, tenants):
        from capstone.Usage_metering.core.exceptions import PaymentRequiredError
        import capstone.Usage_metering.core.database as db
        t = tenants.create_tenant("Expired Corp", plan="free")
        # Mark subscription as canceled
        import sqlite3
        with db.get_db() as conn:
            conn.execute(
                "UPDATE tenants SET subscription_status='canceled' WHERE tenant_id=?",
                (t["tenant_id"],)
            )
            conn.commit()
        with pytest.raises(PaymentRequiredError):
            quota.check_and_consume(t["tenant_id"], "api_call", 1, "key_cancelled")


# ═══════════════════════════════════════════════════════════════════════════
# 5. STRIPE WEBHOOK HMAC VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════

class TestStripeWebhook:
    def _make_stripe_sig(self, payload: str, secret: str) -> str:
        timestamp = str(int(time.time()))
        signed = f"{timestamp}.{payload}"
        sig = hmac.new(secret.encode(), signed.encode(), hashlib.sha256).hexdigest()
        return f"t={timestamp},v1={sig}"

    def test_valid_signature_checkout_completed(self, stripe, tenants):
        t = tenants.create_tenant("Stripe Corp", plan="free")
        payload = json.dumps({
            "id": "evt_checkout_001",
            "type": "checkout.session.completed",
            "data": {"object": {
                "customer": "cus_test_001",
                "subscription": "sub_test_001",
                "metadata": {"tenant_id": t["tenant_id"]},
            }}
        })
        from capstone.Usage_metering.core.config import STRIPE_WEBHOOK_SECRET
        sig = self._make_stripe_sig(payload, STRIPE_WEBHOOK_SECRET)
        success, msg, result = stripe.process(payload, sig)
        assert success is True, f"Valid webhook rejected: {msg}"
        assert result.get("new_plan") == "pro"

    def test_forged_signature_rejected(self, stripe):
        payload = json.dumps({"id": "evt_forged", "type": "checkout.session.completed", "data": {"object": {}}})
        forged_sig = "t=9999999999,v1=deadbeefdeadbeefdeadbeef"
        success, msg, _ = stripe.process(payload, forged_sig)
        assert success is False, "Forged webhook must be rejected"
        assert "invalid" in msg.lower() or "signature" in msg.lower()

    def test_subscription_deleted_downgrades_to_free(self, stripe, tenants):
        from capstone.Usage_metering.core.config import STRIPE_WEBHOOK_SECRET
        import capstone.Usage_metering.core.database as db
        t = tenants.create_tenant("Downgrade Corp", plan="pro")
        # Set a subscription ID
        with db.get_db() as conn:
            conn.execute(
                "UPDATE tenants SET stripe_subscription_id='sub_downgrade_test' WHERE tenant_id=?",
                (t["tenant_id"],)
            )
            conn.commit()
        payload = json.dumps({
            "id": "evt_delete_001",
            "type": "customer.subscription.deleted",
            "data": {"object": {"id": "sub_downgrade_test", "status": "canceled"}}
        })
        sig = self._make_stripe_sig(payload, STRIPE_WEBHOOK_SECRET)
        success, msg, result = stripe.process(payload, sig)
        assert success is True
        updated = tenants.get_tenant(t["tenant_id"])
        assert updated["plan"] == "free"
        assert updated["subscription_status"] == "canceled"

    def test_duplicate_event_deduplicated(self, stripe):
        from capstone.Usage_metering.core.config import STRIPE_WEBHOOK_SECRET
        payload = json.dumps({"id": "evt_dedup_stripe", "type": "invoice.payment_succeeded", "data": {"object": {}}})
        sig = self._make_stripe_sig(payload, STRIPE_WEBHOOK_SECRET)
        success1, _, _ = stripe.process(payload, sig)
        success2, msg2, _ = stripe.process(payload, sig)
        assert success1 is True
        assert success2 is True
        assert "already" in msg2.lower() or "duplicate" in msg2.lower()


# ═══════════════════════════════════════════════════════════════════════════
# 6. MULTI-TENANT ISOLATION
# ═══════════════════════════════════════════════════════════════════════════

class TestMultiTenantIsolation:
    def test_usage_is_scoped_to_tenant(self, quota, tenants):
        ta = tenants.create_tenant("Tenant Alpha", plan="pro")
        tb = tenants.create_tenant("Tenant Beta", plan="pro")
        quota.check_and_consume(ta["tenant_id"], "api_call", 100, "alpha_key")
        quota.check_and_consume(tb["tenant_id"], "api_call", 200, "beta_key")
        
        summary_a = quota.get_usage_summary(ta["tenant_id"])
        summary_b = quota.get_usage_summary(tb["tenant_id"])
        
        assert summary_a["api_calls"]["used"] == 100
        assert summary_b["api_calls"]["used"] == 200, "Tenant B should have independent usage"

    def test_invoice_only_shows_own_events(self, quota, tenants, calc):
        ta = tenants.create_tenant("Invoice Alpha", plan="pro")
        tb = tenants.create_tenant("Invoice Beta", plan="pro")
        quota.check_and_consume(ta["tenant_id"], "api_call", 50, "inv_a")
        quota.check_and_consume(tb["tenant_id"], "api_call", 50, "inv_b")
        
        invoice_a = calc.monthly_invoice(ta["tenant_id"])
        # Alpha's invoice should only reflect Alpha's 50 calls
        assert invoice_a["total_micro_cents"] == 50 * 1000, \
            f"Invoice shows wrong amount: {invoice_a['total_micro_cents']}"
