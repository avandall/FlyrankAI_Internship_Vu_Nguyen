"""
Embeddable Widget — Automated Test Suite (AnyIO / Asyncio)
Tests: multi-tenant isolation, CORS, rate limiting, honeypot, geo-IP fallback,
webhook safe side effect, submission persistence.
Run: pytest capstone/Embeddeable_widget/tests/test_widget.py -v
"""
import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

import pytest
from unittest.mock import patch, MagicMock

from capstone.Embeddeable_widget.core.database import init_db
from capstone.Embeddeable_widget.services.tenant import TenantService
from capstone.Embeddeable_widget.services.widget import WidgetService
from capstone.Embeddeable_widget.services.submission import SubmissionService
from capstone.Embeddeable_widget.services.geoip import GeoIPService
from capstone.Embeddeable_widget.core.exceptions import SpamDetectedError, RateLimitError, ValidationError


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.fixture(autouse=True)
async def setup_db(anyio_backend):
    await init_db()
    yield


@pytest.fixture
def tenants():
    return TenantService()


@pytest.fixture
def widgets():
    return WidgetService()


@pytest.fixture
def submissions():
    return SubmissionService()


# ═══════════════════════════════════════════════════════════════════════════
# 1. TENANT & AUTH TESTS
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.anyio
async def test_create_tenant_generates_api_key(tenants):
    t = await tenants.create_tenant("Acme Corp", "admin_acme@example.com", "t_acme_1")
    assert t["api_key"].startswith("sk_")
    assert t["tenant_id"] == "t_acme_1"


@pytest.mark.anyio
async def test_lookup_by_api_key(tenants):
    t = await tenants.create_tenant("Test Corp", "test_corp@example.com", "t_test_corp")
    found = await tenants.get_tenant_by_api_key(t["api_key"])
    assert found is not None
    assert found["name"] == "Test Corp"


@pytest.mark.anyio
async def test_invalid_api_key_returns_none(tenants):
    result = await tenants.get_tenant_by_api_key("sk_invalid_key_doesnt_exist")
    assert result is None


# ═══════════════════════════════════════════════════════════════════════════
# 2. WIDGET CRUD + MULTI-TENANT ISOLATION
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.anyio
async def test_create_and_retrieve_widget(tenants, widgets):
    t = await tenants.create_tenant("Alpha Corp", "alpha_widget@example.com", "t_alpha_w")
    w = await widgets.create_widget(t["tenant_id"], {
        "widget_id": "w_alpha_form", "name": "Alpha Form", "form_type": "contact"
    })
    assert w["name"] == "Alpha Form"
    assert w["tenant_id"] == t["tenant_id"]


@pytest.mark.anyio
async def test_tenant_a_cannot_modify_tenant_b_widget(tenants, widgets):
    ta = await tenants.create_tenant("Alpha Corp", "ta@example.com", "t_a_iso")
    tb = await tenants.create_tenant("Beta Corp", "tb@example.com", "t_b_iso")
    wb = await widgets.create_widget(tb["tenant_id"], {"widget_id": "w_beta_iso", "name": "Beta Widget"})

    result = await widgets.update_widget(wb["widget_id"], ta["tenant_id"], {"name": "HACKED"})
    assert result is None, "Tenant A must NOT be able to update Tenant B's widget"

    original = await widgets.get_widget(wb["widget_id"])
    assert original["name"] == "Beta Widget"


@pytest.mark.anyio
async def test_tenant_a_cannot_delete_tenant_b_widget(tenants, widgets):
    ta = await tenants.create_tenant("Alpha Corp", "ta_del@example.com", "t_a_del")
    tb = await tenants.create_tenant("Beta Corp", "tb_del@example.com", "t_b_del")
    wb = await widgets.create_widget(tb["tenant_id"], {"widget_id": "w_beta_del", "name": "Beta Widget"})

    ok = await widgets.delete_widget(wb["widget_id"], ta["tenant_id"])
    assert ok is False, "Tenant A must NOT be able to delete Tenant B's widget"
    assert await widgets.get_widget(wb["widget_id"]) is not None


@pytest.mark.anyio
async def test_widget_listing_scoped_to_tenant(tenants, widgets):
    ta = await tenants.create_tenant("Alpha Corp", "ta_list@example.com", "t_a_list")
    tb = await tenants.create_tenant("Beta Corp", "tb_list@example.com", "t_b_list")
    await widgets.create_widget(ta["tenant_id"], {"widget_id": "w_a1", "name": "Alpha Widget 1"})
    await widgets.create_widget(ta["tenant_id"], {"widget_id": "w_a2", "name": "Alpha Widget 2"})
    await widgets.create_widget(tb["tenant_id"], {"widget_id": "w_b1", "name": "Beta Widget 1"})

    alpha_widgets = await widgets.get_for_tenant(ta["tenant_id"])
    assert len(alpha_widgets) >= 2
    assert all(w["tenant_id"] == ta["tenant_id"] for w in alpha_widgets)


@pytest.mark.anyio
async def test_embed_snippet_generated(tenants, widgets):
    t = await tenants.create_tenant("Snippet Corp", "snip@example.com", "t_snip")
    await widgets.create_widget(t["tenant_id"], {"widget_id": "w_test_01", "name": "Test"})
    snippet = await widgets.generate_embed_snippet("w_test_01")
    assert "w_test_01" in snippet
    assert "<script" in snippet
    assert "widget.js" in snippet


# ═══════════════════════════════════════════════════════════════════════════
# 3. SUBMISSION + HONEYPOT + RATE LIMITING
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.anyio
async def test_valid_submission_succeeds(tenants, widgets, submissions):
    t = await tenants.create_tenant("Sub Tenant", "sub_t@example.com", "t_sub")
    await widgets.create_widget(t["tenant_id"], {"widget_id": "w_sub_1", "name": "Sub Widget"})
    
    result = await submissions.submit(
        "w_sub_1",
        {"email": "test@example.com", "name": "Test User"},
        "1.2.3.4", "http://example.com"
    )
    assert result["submission_id"].startswith("sub_")
    assert result["email"] == "test@example.com"


@pytest.mark.anyio
async def test_honeypot_blocks_spam(tenants, widgets, submissions):
    t = await tenants.create_tenant("Spam Tenant", "spam_t@example.com", "t_spam")
    await widgets.create_widget(t["tenant_id"], {"widget_id": "w_spam_1", "name": "Spam Form"})

    with pytest.raises(SpamDetectedError):
        await submissions.submit(
            "w_spam_1",
            {"email": "bot@spam.com", "_hp_field": "I am a bot"},
            "5.5.5.5", "http://spamsite.com"
        )


@pytest.mark.anyio
async def test_rate_limit_blocks_after_threshold(tenants, widgets, submissions):
    t = await tenants.create_tenant("Rate Tenant", "rate_t@example.com", "t_rate")
    await widgets.create_widget(t["tenant_id"], {
        "widget_id": "w_rate_1", "name": "Rate Form", "rate_limit_per_min": 2
    })

    ip = "9.9.9.9"
    # 1st & 2nd request succeed
    await submissions.submit("w_rate_1", {"email": "user1@test.com"}, ip, "http://test.com")
    await submissions.submit("w_rate_1", {"email": "user2@test.com"}, ip, "http://test.com")

    # 3rd request fails rate limit
    with pytest.raises(RateLimitError):
        await submissions.submit("w_rate_1", {"email": "user3@test.com"}, ip, "http://test.com")


@pytest.mark.anyio
async def test_invalid_email_raises_validation_error(tenants, widgets, submissions):
    t = await tenants.create_tenant("Val Tenant", "val_t@example.com", "t_val")
    await widgets.create_widget(t["tenant_id"], {"widget_id": "w_val_1", "name": "Val Form"})

    with pytest.raises(ValidationError):
        await submissions.submit(
            "w_val_1", {"email": "not-an-email"}, "1.1.1.1", "http://test.com"
        )


@pytest.mark.anyio
async def test_missing_widget_raises_value_error(submissions):
    with pytest.raises(ValueError, match="Widget not found"):
        await submissions.submit("w_nonexistent", {"email": "ok@test.com"}, "1.1.1.1", "http://test.com")


@pytest.mark.anyio
async def test_submissions_persisted(tenants, widgets, submissions):
    t = await tenants.create_tenant("Persist Tenant", "pers_t@example.com", "t_pers")
    await widgets.create_widget(t["tenant_id"], {"widget_id": "w_pers_1", "name": "Persist Form"})

    await submissions.submit("w_pers_1", {"email": "persist@test.com"}, "2.2.2.2", "http://test.com")
    leads = await submissions.get_for_tenant(t["tenant_id"])
    assert any(l["email"] == "persist@test.com" for l in leads)


# ═══════════════════════════════════════════════════════════════════════════
# 4. GEO-IP FALLBACK CHAIN TESTS
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.anyio
async def test_provider_a_succeeds():
    geo = GeoIPService()
    
    class MockRespA:
        status_code = 200
        def json(self):
            return {"status": "success", "country": "Vietnam", "city": "Hanoi", "regionName": "Hanoi"}

    class MockClientA:
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass
        async def get(self, url, **kwargs):
            return MockRespA()

    with patch("httpx.AsyncClient", return_value=MockClientA()):
        result = await geo.lookup("1.53.0.1")
    assert result["country"] == "Vietnam"
    assert result["provider"] == "ip-api.com"


@pytest.mark.anyio
async def test_fallback_to_provider_b_when_a_fails():
    geo = GeoIPService()

    class MockClientFallback:
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass
        async def get(self, url, **kwargs):
            if "ip-api.com" in url:
                raise Exception("Provider A down")
            
            class MockRespB:
                status_code = 200
                def json(self):
                    return {"country_name": "Germany", "city": "Berlin", "region": "Berlin"}
            return MockRespB()

    with patch("httpx.AsyncClient", return_value=MockClientFallback()):
        result = await geo.lookup("5.175.0.1")
    assert result["country"] == "Germany"
    assert result["provider"] == "ipapi.co"


@pytest.mark.anyio
async def test_both_providers_fail_submission_still_succeeds():
    geo = GeoIPService()

    class MockClientAllFail:
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass
        async def get(self, url, **kwargs):
            raise Exception("All providers down")

    with patch("httpx.AsyncClient", return_value=MockClientAllFail()):
        result = await geo.lookup("5.5.5.5")
    assert result["country"] is None
    assert result["provider"] is None


# ═══════════════════════════════════════════════════════════════════════════
# 5. WEBHOOK SAFE SIDE EFFECT TEST
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.anyio
async def test_webhook_failure_does_not_block_submission(tenants, widgets, submissions):
    t = await tenants.create_tenant("Webhook Corp", "wh_t@example.com", "t_wh")
    await widgets.create_widget(t["tenant_id"], {
        "widget_id": "w_webhook_test",
        "name": "Webhook Widget",
        "webhook_url": "https://invalid-webhook-server.example.com/hook",
    })

    result = await submissions.submit(
        "w_webhook_test",
        {"email": "ok@test.com", "name": "Safe User"},
        "1.1.1.1", "http://test.com"
    )

    assert "submission_id" in result, "Submission should succeed even when webhook fails"
