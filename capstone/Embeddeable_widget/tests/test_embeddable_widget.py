"""
Tests for Embeddable Widget & Lead-Capture Platform.
Rebuilt per Capstone Spec.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
import pytest
from pathlib import Path

# Redirect DB to temporary location for tests
os.environ['WIDGET_TEST_DB'] = str(Path(__file__).parent / 'test_widget.db')

from capstone.Embeddeable_widget.core.database import init_db
from capstone.Embeddeable_widget.services.tenant import TenantService
from capstone.Embeddeable_widget.services.widget import WidgetService
from capstone.Embeddeable_widget.services.submission import SubmissionService
from capstone.Embeddeable_widget.services.geoip import GeoIPService
from capstone.Embeddeable_widget.services.abuse import AbuseProtection
from capstone.Embeddeable_widget.services.webhook import WebhookService
from capstone.Embeddeable_widget.core.exceptions import (
    SpamDetectedError, RateLimitError, ValidationError, MultiTenantAccessDenied,
)


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    import capstone.Embeddeable_widget.core.database as db
    test_db = tmp_path / "test.db"
    monkeypatch.setattr(db, 'DB_PATH', test_db)
    init_db()
    yield

@pytest.fixture
def tenant_svc():
    return TenantService()

@pytest.fixture
def widget_svc():
    return WidgetService()

@pytest.fixture
def submission_svc():
    return SubmissionService()


def test_multi_tenant_isolation(tenant_svc, widget_svc):
    t1 = tenant_svc.create_tenant("Tenant Alpha", "alpha@test.com", "t_alpha")
    t2 = tenant_svc.create_tenant("Tenant Beta", "beta@test.com", "t_beta")

    w1 = widget_svc.create_widget("t_alpha", {"widget_id": "w_101", "name": "Alpha Widget"})
    assert w1["tenant_id"] == "t_alpha"

    # Widget list per tenant
    alpha_widgets = widget_svc.get_for_tenant("t_alpha")
    beta_widgets = widget_svc.get_for_tenant("t_beta")

    assert len(alpha_widgets) == 1
    assert len(beta_widgets) == 0

    # Cross-tenant update blocked
    updated = widget_svc.update_widget("w_101", "t_beta", {"name": "Hacked Widget"})
    assert updated is None  # Blocked


def test_embed_snippet_generation(tenant_svc, widget_svc):
    tenant_svc.create_tenant("Tenant Alpha", "alpha@test.com", "t_alpha")
    widget_svc.create_widget("t_alpha", {"widget_id": "w_101", "name": "Form"})
    snippet = widget_svc.generate_embed_snippet("w_101", "http://localhost:8002")
    assert '<script src="http://localhost:8002/widget.js?id=w_101&v=1"' in snippet


def test_public_submission_happy_path(tenant_svc, widget_svc, submission_svc):
    tenant_svc.create_tenant("Tenant Alpha", "alpha@test.com", "t_alpha")
    widget_svc.create_widget("t_alpha", {"widget_id": "w_201", "name": "Contact Form"})

    sub = submission_svc.submit(
        widget_id="w_201",
        data={"email": "alice@example.com", "name": "Alice Smith", "message": "Hello"},
        source_ip="127.0.0.1",
        source_origin="http://localhost:5500",
    )
    assert sub["submission_id"].startswith("sub_")
    assert sub["email"] == "alice@example.com"
    assert sub["country"] == "Local"


def test_honeypot_spam_blocking(tenant_svc, widget_svc, submission_svc):
    tenant_svc.create_tenant("Tenant Alpha", "alpha@test.com", "t_alpha")
    widget_svc.create_widget("t_alpha", {"widget_id": "w_202", "name": "Form"})

    with pytest.raises(SpamDetectedError):
        submission_svc.submit(
            widget_id="w_202",
            data={"email": "bot@spam.com", "_hp_field": "I am a bot filling hidden inputs"},
            source_ip="5.6.7.8",
            source_origin="http://spam-site.com",
        )


def test_rate_limiting(tenant_svc, widget_svc, submission_svc):
    tenant_svc.create_tenant("Tenant Alpha", "alpha@test.com", "t_alpha")
    widget_svc.create_widget("t_alpha", {"widget_id": "w_204", "name": "Rate Form", "rate_limit_per_min": 2})

    ip = "10.0.0.99"
    data = {"email": "user@example.com"}

    # 1st & 2nd succeed
    submission_svc.submit("w_204", data, source_ip=ip, source_origin="http://test.com")
    submission_svc.submit("w_204", data, source_ip=ip, source_origin="http://test.com")

    # 3rd fails rate limit
    with pytest.raises(RateLimitError):
        submission_svc.submit("w_204", data, source_ip=ip, source_origin="http://test.com")


def test_geo_enrichment_fallback_chain(monkeypatch):
    """Test Geo-IP fallback logic."""
    geo = GeoIPService()
    # Mock requests.get to simulate primary & secondary failure
    def mock_fail(*args, **kwargs):
        raise ConnectionError("Network down")
    monkeypatch.setattr("requests.get", mock_fail)

    result = geo.lookup("8.8.8.8")
    assert result["country"] is None
    assert result["city"] is None


def test_webhook_failure_does_not_fail_submission(tenant_svc, widget_svc, submission_svc, monkeypatch):
    tenant_svc.create_tenant("Tenant Alpha", "alpha@test.com", "t_alpha")
    widget_svc.create_widget("t_alpha", {
        "widget_id": "w_206", "name": "Webhook Form",
        "webhook_url": "https://invalid-webhook-destination-xyz.com/hook"
    })

    # Webhook fails due to invalid destination, but submission succeeds!
    sub = submission_svc.submit(
        widget_id="w_206",
        data={"email": "carol@example.com", "name": "Carol"},
        source_ip="127.0.0.1",
        source_origin="http://example.com",
    )
    assert sub["submission_id"].startswith("sub_")
    assert sub["email"] == "carol@example.com"
    assert "failed" in sub["webhook_status"]
