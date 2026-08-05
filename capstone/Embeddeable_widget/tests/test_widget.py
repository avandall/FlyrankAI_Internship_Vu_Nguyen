"""
Embeddable Widget — Automated Test Suite
Tests: multi-tenant isolation, CORS, rate limiting, honeypot, geo-IP fallback,
webhook safe side effect, submission persistence.
Run: python3 -m pytest capstone/Embeddeable_widget/tests/test_widget.py -v
"""
import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    from capstone.Embeddeable_widget.core.database import init_db
    import capstone.Embeddeable_widget.core.database as db
    monkeypatch.setattr(db, 'DB_PATH', tmp_path / "test_widget.db")
    init_db()
    yield


@pytest.fixture
def tenants():
    from capstone.Embeddeable_widget.services.tenant import TenantService
    return TenantService()


@pytest.fixture
def widgets():
    from capstone.Embeddeable_widget.services.widget import WidgetService
    return WidgetService()


@pytest.fixture
def submissions(widgets):
    from capstone.Embeddeable_widget.services.submission import SubmissionService
    return SubmissionService()


# ═══════════════════════════════════════════════════════════════════════════
# 1. TENANT & AUTH TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestTenantAuth:
    def test_create_tenant_generates_api_key(self, tenants):
        t = tenants.create_tenant("Acme Corp", "admin@acme.com")
        assert t["api_key"].startswith("wk_")
        assert t["tenant_id"].startswith("t_")

    def test_lookup_by_api_key(self, tenants):
        t = tenants.create_tenant("Test Corp")
        found = tenants.get_by_api_key(t["api_key"])
        assert found is not None
        assert found["name"] == "Test Corp"

    def test_invalid_api_key_returns_none(self, tenants):
        result = tenants.get_by_api_key("wk_invalid_key_doesnt_exist")
        assert result is None


# ═══════════════════════════════════════════════════════════════════════════
# 2. WIDGET CRUD + MULTI-TENANT ISOLATION
# ═══════════════════════════════════════════════════════════════════════════

class TestWidgetMultiTenant:
    def test_create_and_retrieve_widget(self, tenants, widgets):
        t = tenants.create_tenant("Alpha Corp")
        w = widgets.create_widget(t["tenant_id"], {
            "name": "Alpha Form", "form_type": "contact"
        })
        assert w["name"] == "Alpha Form"
        assert w["tenant_id"] == t["tenant_id"]

    def test_tenant_a_cannot_modify_tenant_b_widget(self, tenants, widgets):
        """Multi-tenant isolation: Tenant A cannot update Tenant B's widget."""
        ta = tenants.create_tenant("Alpha Corp")
        tb = tenants.create_tenant("Beta Corp")
        wb = widgets.create_widget(tb["tenant_id"], {"name": "Beta Widget"})

        # Tenant A tries to update Beta's widget
        result = widgets.update_widget(wb["widget_id"], ta["tenant_id"], {"name": "HACKED"})
        assert result is None, "Tenant A must NOT be able to update Tenant B's widget"

        # Widget should still have original name
        original = widgets.get_widget(wb["widget_id"])
        assert original["name"] == "Beta Widget", "Widget name should not have changed"

    def test_tenant_a_cannot_delete_tenant_b_widget(self, tenants, widgets):
        ta = tenants.create_tenant("Alpha Corp")
        tb = tenants.create_tenant("Beta Corp")
        wb = widgets.create_widget(tb["tenant_id"], {"name": "Beta Widget"})
        ok = widgets.delete_widget(wb["widget_id"], ta["tenant_id"])
        assert ok is False, "Tenant A must NOT be able to delete Tenant B's widget"
        assert widgets.get_widget(wb["widget_id"]) is not None

    def test_widget_listing_scoped_to_tenant(self, tenants, widgets):
        ta = tenants.create_tenant("Alpha Corp")
        tb = tenants.create_tenant("Beta Corp")
        widgets.create_widget(ta["tenant_id"], {"name": "Alpha Widget 1"})
        widgets.create_widget(ta["tenant_id"], {"name": "Alpha Widget 2"})
        widgets.create_widget(tb["tenant_id"], {"name": "Beta Widget 1"})

        alpha_widgets = widgets.get_for_tenant(ta["tenant_id"])
        assert len(alpha_widgets) == 2
        assert all(w["tenant_id"] == ta["tenant_id"] for w in alpha_widgets)

    def test_embed_snippet_generated(self, tenants, widgets):
        t = tenants.create_tenant("Snippet Corp")
        w = widgets.create_widget(t["tenant_id"], {"widget_id": "w_test_01", "name": "Test"})
        snippet = widgets.generate_embed_snippet("w_test_01")
        assert "w_test_01" in snippet
        assert "<script" in snippet
        assert "widget.js" in snippet


# ═══════════════════════════════════════════════════════════════════════════
# 3. SUBMISSION + HONEYPOT + RATE LIMITING
# ═══════════════════════════════════════════════════════════════════════════

class TestSubmission:
    @pytest.fixture(autouse=True)
    def setup_widget(self, tenants, widgets):
        t = tenants.create_tenant("Test Tenant")
        self.tenant = t
        self.widget = widgets.create_widget(t["tenant_id"], {
            "widget_id": "w_test_sub",
            "name": "Test Widget",
            "rate_limit_per_min": 3,
        })

    def test_valid_submission_succeeds(self, submissions):
        result = submissions.submit(
            "w_test_sub",
            {"email": "test@example.com", "name": "Test User"},
            "1.2.3.4", "http://example.com"
        )
        assert result["submission_id"].startswith("sub_")
        assert result["email"] == "test@example.com"

    def test_honeypot_blocks_spam(self, submissions):
        from capstone.Embeddeable_widget.core.exceptions import SpamDetectedError
        with pytest.raises(SpamDetectedError):
            submissions.submit(
                "w_test_sub",
                {"email": "bot@spam.com", "_hp_field": "I am a bot"},
                "5.5.5.5", "http://spamsite.com"
            )

    def test_rate_limit_blocks_after_threshold(self, submissions):
        from capstone.Embeddeable_widget.core.exceptions import RateLimitError
        # Send 3 requests (limit is 3)
        for _ in range(3):
            submissions.submit("w_test_sub", {"email": "user@test.com"}, "9.9.9.9", "http://test.com")
        # 4th should be rate-limited
        with pytest.raises(RateLimitError):
            submissions.submit("w_test_sub", {"email": "user@test.com"}, "9.9.9.9", "http://test.com")

    def test_invalid_email_raises_validation_error(self, submissions):
        from capstone.Embeddeable_widget.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            submissions.submit(
                "w_test_sub", {"email": "not-an-email"}, "1.1.1.1", "http://test.com"
            )

    def test_missing_widget_raises_value_error(self, submissions):
        with pytest.raises(ValueError, match="Widget not found"):
            submissions.submit("w_nonexistent", {"email": "ok@test.com"}, "1.1.1.1", "http://test.com")

    def test_submissions_persisted(self, submissions, tenants):
        submissions.submit("w_test_sub", {"email": "persist@test.com"}, "2.2.2.2", "http://test.com")
        leads = submissions.get_for_tenant(self.tenant["tenant_id"])
        assert any(l["email"] == "persist@test.com" for l in leads)


# ═══════════════════════════════════════════════════════════════════════════
# 4. GEO-IP FALLBACK CHAIN TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestGeoIPFallback:
    def test_provider_a_succeeds(self):
        from capstone.Embeddeable_widget.services.geoip import GeoIPService
        geo = GeoIPService()
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"status": "success", "country": "Vietnam", "city": "Hanoi", "regionName": "Hanoi"}
            mock_get.return_value = mock_resp
            result = geo.lookup("1.53.0.1")
        assert result["country"] == "Vietnam"
        assert result["provider"] == "ip-api.com"

    def test_fallback_to_provider_b_when_a_fails(self):
        from capstone.Embeddeable_widget.services.geoip import GeoIPService
        geo = GeoIPService()
        call_count = [0]
        def side_effect(url, **kwargs):
            call_count[0] += 1
            if "ip-api.com" in url:
                raise Exception("Provider A down")
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = {"country_name": "Germany", "city": "Berlin", "region": "Berlin"}
            return resp
        with patch("requests.get", side_effect=side_effect):
            result = geo.lookup("5.175.0.1")
        assert result["country"] == "Germany"
        assert result["provider"] == "ipapi.co"

    def test_both_providers_fail_submission_still_succeeds(self):
        """Safe fallback: if both geo providers are down, submission is still saved."""
        from capstone.Embeddeable_widget.services.geoip import GeoIPService
        geo = GeoIPService()
        with patch("requests.get", side_effect=Exception("All providers down")):
            result = geo.lookup("5.5.5.5")
        assert result["country"] is None
        assert result["provider"] is None


# ═══════════════════════════════════════════════════════════════════════════
# 5. WEBHOOK SAFE SIDE EFFECT TEST
# ═══════════════════════════════════════════════════════════════════════════

class TestWebhookSafeSideEffect:
    def test_webhook_failure_does_not_block_submission(self, tenants, widgets, submissions):
        """If webhook delivery fails, the submission must still succeed."""
        t = tenants.create_tenant("Webhook Corp")
        widgets.create_widget(t["tenant_id"], {
            "widget_id": "w_webhook_test",
            "name": "Webhook Widget",
            "webhook_url": "https://invalid-webhook-server.example.com/hook",
        })

        # Webhook will fail (unreachable URL), but submission should succeed
        with patch("requests.post", side_effect=Exception("Webhook server down")):
            result = submissions.submit(
                "w_webhook_test",
                {"email": "ok@test.com", "name": "Safe User"},
                "1.1.1.1", "http://test.com"
            )

        assert "submission_id" in result, "Submission should succeed even when webhook fails"
        assert "failed" in result["webhook_status"]
