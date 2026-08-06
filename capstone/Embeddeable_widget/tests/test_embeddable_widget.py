"""
Tests for Embeddable Widget & Lead-Capture Platform.
Async PostgreSQL version.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
import pytest
from unittest.mock import patch

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
def tenant_svc():
    return TenantService()

@pytest.fixture
def widget_svc():
    return WidgetService()

@pytest.fixture
def submission_svc():
    return SubmissionService()


@pytest.mark.anyio
async def test_multi_tenant_isolation(tenant_svc, widget_svc):
    await tenant_svc.create_tenant("Tenant Alpha", "alpha_emb@test.com", "t_alpha_emb")
    await tenant_svc.create_tenant("Tenant Beta", "beta_emb@test.com", "t_beta_emb")

    w1 = await widget_svc.create_widget("t_alpha_emb", {"widget_id": "w_101_emb", "name": "Alpha Widget"})
    assert w1["tenant_id"] == "t_alpha_emb"

    # Widget list per tenant
    alpha_widgets = await widget_svc.get_for_tenant("t_alpha_emb")
    beta_widgets = await widget_svc.get_for_tenant("t_beta_emb")

    assert any(w["widget_id"] == "w_101_emb" for w in alpha_widgets)
    assert not any(w["widget_id"] == "w_101_emb" for w in beta_widgets)

    # Cross-tenant update blocked
    updated = await widget_svc.update_widget("w_101_emb", "t_beta_emb", {"name": "Hacked Widget"})
    assert updated is None  # Blocked


@pytest.mark.anyio
async def test_embed_snippet_generation(tenant_svc, widget_svc):
    await tenant_svc.create_tenant("Tenant Alpha", "alpha_snip@test.com", "t_alpha_snip")
    await widget_svc.create_widget("t_alpha_snip", {"widget_id": "w_101_snip", "name": "Form"})
    snippet = await widget_svc.generate_embed_snippet("w_101_snip", "http://localhost:8002")
    assert '<script src="http://localhost:8002/widget.js?id=w_101_snip&v=' in snippet


@pytest.mark.anyio
async def test_public_submission_happy_path(tenant_svc, widget_svc, submission_svc):
    await tenant_svc.create_tenant("Tenant Alpha", "alpha_pub@test.com", "t_alpha_pub")
    await widget_svc.create_widget("t_alpha_pub", {"widget_id": "w_201_pub", "name": "Contact Form"})

    sub = await submission_svc.submit(
        widget_id="w_201_pub",
        data={"email": "alice@example.com", "name": "Alice Smith", "message": "Hello"},
        source_ip="127.0.0.1",
        source_origin="http://localhost:5500",
    )
    assert sub["submission_id"].startswith("sub_")
    assert sub["email"] == "alice@example.com"
    assert sub["country"] == "Local"


@pytest.mark.anyio
async def test_honeypot_spam_blocking(tenant_svc, widget_svc, submission_svc):
    await tenant_svc.create_tenant("Tenant Alpha", "alpha_hp@test.com", "t_alpha_hp")
    await widget_svc.create_widget("t_alpha_hp", {"widget_id": "w_202_hp", "name": "Form"})

    with pytest.raises(SpamDetectedError):
        await submission_svc.submit(
            widget_id="w_202_hp",
            data={"email": "bot@spam.com", "_hp_field": "I am a bot filling hidden inputs"},
            source_ip="5.6.7.8",
            source_origin="http://spam-site.com",
        )


@pytest.mark.anyio
async def test_rate_limiting(tenant_svc, widget_svc, submission_svc):
    await tenant_svc.create_tenant("Tenant Alpha", "alpha_rl@test.com", "t_alpha_rl")
    await widget_svc.create_widget("t_alpha_rl", {"widget_id": "w_204_rl", "name": "Rate Form", "rate_limit_per_min": 2})

    ip = "10.0.0.99"
    data = {"email": "user@example.com"}

    # 1st & 2nd succeed
    await submission_svc.submit("w_204_rl", data, source_ip=ip, source_origin="http://test.com")
    await submission_svc.submit("w_204_rl", data, source_ip=ip, source_origin="http://test.com")

    # 3rd fails rate limit
    with pytest.raises(RateLimitError):
        await submission_svc.submit("w_204_rl", data, source_ip=ip, source_origin="http://test.com")


@pytest.mark.anyio
async def test_geo_enrichment_fallback_chain():
    geo = GeoIPService()

    class MockClientAllFail:
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass
        async def get(self, url, **kwargs):
            raise Exception("Network down")

    with patch("httpx.AsyncClient", return_value=MockClientAllFail()):
        result = await geo.lookup("8.8.8.8")
    assert result["country"] is None
    assert result["city"] is None


@pytest.mark.anyio
async def test_webhook_failure_does_not_fail_submission(tenant_svc, widget_svc, submission_svc):
    await tenant_svc.create_tenant("Tenant Alpha", "alpha_wh@test.com", "t_alpha_wh")
    await widget_svc.create_widget("t_alpha_wh", {
        "widget_id": "w_206_wh", "name": "Webhook Form",
        "webhook_url": "https://invalid-webhook-destination-xyz.com/hook"
    })

    sub = await submission_svc.submit(
        widget_id="w_206_wh",
        data={"email": "carol@example.com", "name": "Carol"},
        source_ip="127.0.0.1",
        source_origin="http://example.com",
    )
    assert sub["submission_id"].startswith("sub_")
    assert sub["email"] == "carol@example.com"
