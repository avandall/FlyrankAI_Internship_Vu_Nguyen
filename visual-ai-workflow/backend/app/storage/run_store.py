"""
In-memory and JSON storage for Workflow Execution Runs
"""

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.models.workflow_schema import WorkflowExecutionResult

_lock = threading.Lock()
_runs: Dict[str, Dict[str, Any]] = {}
DATA_DIR = Path("/home/avandall/project/FlyrankAI/visual-ai-workflow/backend/data")

def init_store():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def create_run(run_id: str, status: str = "pending") -> Dict[str, Any]:
    with _lock:
        now = datetime.now(timezone.utc).isoformat()
        record = {
            "run_id": run_id,
            "status": status,
            "final_decision": None,
            "visited_nodes": [],
            "active_edges": [],
            "trace": [],
            "error": None,
            "created_at": now,
            "completed_at": None,
        }
        _runs[run_id] = record
        return record

def update_run(
    run_id: str,
    status: Optional[str] = None,
    final_decision: Optional[str] = None,
    visited_nodes: Optional[List[str]] = None,
    active_edges: Optional[List[str]] = None,
    trace_step: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    with _lock:
        if run_id not in _runs:
            return None
        record = _runs[run_id]
        if status:
            record["status"] = status
            if status in ["completed", "failed"]:
                record["completed_at"] = datetime.now(timezone.utc).isoformat()
        if final_decision is not None:
            record["final_decision"] = final_decision
        if visited_nodes is not None:
            record["visited_nodes"] = visited_nodes
        if active_edges is not None:
            record["active_edges"] = active_edges
        if trace_step is not None:
            record["trace"].append(trace_step)
        if error is not None:
            record["error"] = error
        return record

def get_run(run_id: str) -> Optional[Dict[str, Any]]:
    with _lock:
        return _runs.get(run_id)

def list_runs() -> List[Dict[str, Any]]:
    with _lock:
        return list(_runs.values())
