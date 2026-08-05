import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
from fastapi.testclient import TestClient
from capstone.AI_Image.main import app

client = TestClient(app)

def test_ai_image_app_routes():
    res1 = client.get("/")
    assert res1.status_code == 200
    assert "AI Image Understanding" in res1.text

    res2 = client.get("/api/images")
    assert res2.status_code == 200
    assert len(res2.json()["images"]) >= 3

    res3 = client.post("/api/match", json={
        "post_id": "p1",
        "title": "Red Fox",
        "text": "A wild red fox standing in forest snow",
        "target_subject": "red fox",
        "target_category": "animal"
    })
    assert res3.status_code == 200
    assert res3.json()["status"] == "MATCHED"
