import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
from fastapi.testclient import TestClient
from capstone.Usage_metering.main import app

client = TestClient(app)

def test_usage_metering_app_routes():
    from capstone.Usage_metering.core.database import init_db
    from capstone.Usage_metering.services.tenant import TenantService
    init_db()
    TenantService().create_tenant("FlyRank Demo (Free)", "demo@flyrank.ai", "free", "t_demo_free")

    # 1. UI Root
    res1 = client.get("/")
    assert res1.status_code == 200
    assert "Usage Metering" in res1.text or "Micro-Cent" in res1.text

    # 2. Get tenant usage
    res2 = client.get("/api/usage/t_demo_free")
    assert res2.status_code == 200
    assert "api_calls" in res2.json()

    # 3. Get plans
    res3 = client.get("/api/plans")
    assert res3.status_code == 200
    assert "plans" in res3.json()

    # 4. Record usage event
    res4 = client.post("/api/usage/record", json={
        "idempotency_key": "ev_app_1001",
        "tenant_id": "t_demo_free",
        "event_type": "api_call",
        "quantity": 1
    })
    assert res4.status_code == 200
    assert res4.json()["status"] == "recorded"

    # 5. Simulate Stripe webhook
    res5 = client.post("/api/webhook/stripe/test", json={
        "tenant_id": "t_demo_free",
        "event_type": "checkout.session.completed"
    })
    assert res5.status_code == 200
    assert res5.json()["status"] == "simulated"
