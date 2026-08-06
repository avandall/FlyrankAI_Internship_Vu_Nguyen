import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
import pytest
from fastapi.testclient import TestClient
from capstone.Embeddeable_widget.main import app


def test_widget_app_routes():
    with TestClient(app) as client:
        # 1. Root dashboard UI
        res1 = client.get("/")
        assert res1.status_code == 200
        assert "Widget" in res1.text or "Embeddable" in res1.text

        # 2. Public Widget Config & Embed snippet
        res2 = client.get("/api/widget/w_demo_flyrank/config")
        assert res2.status_code == 200
        assert "embed_snippet" in res2.json()

        # 3. Serve versioned widget.js
        res_js = client.get("/widget.js?id=w_demo_flyrank&v=1")
        assert res_js.status_code == 200
        assert "application/javascript" in res_js.headers["content-type"]
        assert "FlyRank Widget" in res_js.text

        # 4. Public submission endpoint
        res3 = client.post("/api/public/submit", json={
            "widget_id": "w_demo_flyrank",
            "name": "Bob",
            "email": "bob@example.com",
            "message": "Hello from test",
        })
        assert res3.status_code == 200
        assert res3.json()["status"] == "success"

        # 5. Customer website simulation test page
        res_test = client.get("/test-embed")
        assert res_test.status_code == 200
        assert "Customer Test Page" in res_test.text
