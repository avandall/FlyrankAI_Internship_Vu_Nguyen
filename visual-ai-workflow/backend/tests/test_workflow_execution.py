"""
Tests for Inngest Workflow Execution & Traversal
"""

import time
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.workflow_schema import (
    WorkflowEdge,
    WorkflowGraph,
    WorkflowNode,
    NodeData,
)

client = TestClient(app)


def get_sample_support_workflow() -> dict:
    return {
        "workflow": {
            "nodes": [
                {
                    "id": "node_1",
                    "type": "decision",
                    "data": {
                        "label": "Triage Inquiry",
                        "prompt": "Is this inquiry related to a technical error or bug?",
                        "node_type": "decision",
                    },
                },
                {
                    "id": "node_tech",
                    "type": "decision",
                    "data": {
                        "label": "Severity Check",
                        "prompt": "Is this issue critical or production blocking?",
                        "node_type": "decision",
                    },
                },
                {
                    "id": "node_sales",
                    "type": "decision",
                    "data": {
                        "label": "Sales Lead",
                        "prompt": "Is the user inquiring about enterprise pricing or plans?",
                        "node_type": "decision",
                    },
                },
                {
                    "id": "node_end_p1",
                    "type": "end",
                    "data": {
                        "label": "Route to P1 On-Call Engineer",
                        "node_type": "end",
                    },
                },
            ],
            "edges": [
                {
                    "id": "e1",
                    "source": "node_1",
                    "target": "node_tech",
                    "sourceHandle": "yes",
                    "label": "YES",
                },
                {
                    "id": "e2",
                    "source": "node_1",
                    "target": "node_sales",
                    "sourceHandle": "no",
                    "label": "NO",
                },
                {
                    "id": "e3",
                    "source": "node_tech",
                    "target": "node_end_p1",
                    "sourceHandle": "yes",
                    "label": "YES",
                },
            ],
        },
        "input_text": "HELP: Our database cluster crashed with out of memory error!",
    }


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_inngest_mount():
    res = client.get("/api/inngest")
    assert res.status_code in [200, 400, 405]


def test_execute_workflow_endpoint_success():
    payload = get_sample_support_workflow()
    res = client.post("/api/workflow/execute", json=payload)
    assert res.status_code == 202
    data = res.json()
    assert "run_id" in data
    assert data["status"] == "pending"
    assert "status_url" in data

    run_id = data["run_id"]
    time.sleep(0.3)

    poll_res = client.get(f"/api/workflow/runs/{run_id}")
    assert poll_res.status_code == 200
    poll_data = poll_res.json()
    assert poll_data["run_id"] == run_id
    assert poll_data["status"] in ["running", "completed"]
    assert len(poll_data["visited_nodes"]) >= 1


def test_execute_workflow_validation_empty_nodes():
    res = client.post(
        "/api/workflow/execute",
        json={"workflow": {"nodes": [], "edges": []}, "input_text": "hello"},
    )
    assert res.status_code == 400
    assert "must contain at least one node" in res.json()["detail"].lower()


def test_execute_workflow_validation_empty_input():
    res = client.post(
        "/api/workflow/execute",
        json={
            "workflow": {
                "nodes": [{"id": "1", "data": {"label": "test", "prompt": "test"}}],
                "edges": [],
            },
            "input_text": "   ",
        },
    )
    assert res.status_code == 400
    assert "input_text cannot be empty" in res.json()["detail"].lower()


def test_poll_nonexistent_run():
    res = client.get("/api/workflow/runs/nonexistent_run_9999")
    assert res.status_code == 404
