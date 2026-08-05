import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
from fastapi.testclient import TestClient
from capstone.Multi_platform.main import app

client = TestClient(app)

def test_multi_platform_app_routes():
    # 1. UI Root
    res1 = client.get("/")
    assert res1.status_code == 200
    assert "Multi-Platform" in res1.text or "Campaign" in res1.text

    # 2. Captions preview
    res2 = client.post("/api/captions/preview", json={
        "title": "Launch Update",
        "content": "Sample blog post text for social media campaign."
    })
    assert res2.status_code == 200
    assert "instagram" in res2.json()["captions"]
    assert "twitter" in res2.json()["captions"]

    # 3. Create campaign
    res3 = client.post("/api/campaigns", data={
        "title": "New Features",
        "content": "Full release notes for the new version",
        "platforms": '["instagram","twitter"]'
    })
    assert res3.status_code == 201
    campaign_id = res3.json()["campaign"]["campaign_id"]

    # 4. Publish campaign
    res4 = client.post(f"/api/campaigns/{campaign_id}/publish")
    assert res4.status_code == 200
    assert "results" in res4.json()

    # 5. Webhook test
    res5 = client.post("/api/webhook/test", json={
        "post_id": "p_test_123",
        "platform": "instagram",
        "forge_signature": False
    })
    assert res5.status_code == 200
    assert res5.json()["signature_valid"] is True
