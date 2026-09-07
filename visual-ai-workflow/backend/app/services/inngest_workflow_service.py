"""
Inngest Workflow Engine for Step-by-Step Graph Traversal
"""

import asyncio
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import inngest

from app.models.workflow_schema import (
    DecisionType,
    NodeExecutionStep,
    WorkflowEdge,
    WorkflowGraph,
    WorkflowNode,
)
from app.services.groq_service import evaluate_decision_node
from app.storage.run_store import create_run, get_run, update_run

logger = logging.getLogger("visual_workflow.inngest")

is_dev = os.getenv("INNGEST_DEV", "1") == "1"
signing_key = os.getenv("INNGEST_SIGNING_KEY", "local")

inngest_client = inngest.Inngest(
    app_id="visual-ai-workflow",
    is_production=not is_dev,
    signing_key=signing_key,
)

@inngest_client.create_function(
    fn_id="execute-ai-workflow",
    trigger=inngest.TriggerEvent(event="ai.workflow/run"),
    retries=2,
)
async def execute_ai_workflow(ctx: inngest.Context) -> Dict[str, Any]:
    """
    Inngest step-by-step workflow orchestrator.
    Traverses graph dynamically: each node execution is isolated in step.run().
    """
    step = ctx.step
    event_data = ctx.event.data if ctx.event else {}
    
    run_id = str(event_data.get("run_id", f"run_{uuid.uuid4().hex[:10]}"))
    workflow_raw = event_data.get("workflow", {})
    input_text = str(event_data.get("input_text", ""))
    
    nodes_map: Dict[str, Dict[str, Any]] = {n["id"]: n for n in workflow_raw.get("nodes", [])}
    edges: List[Dict[str, Any]] = workflow_raw.get("edges", [])
    
    update_run(run_id, status="running")
    
    # 1. Find Start Node
    current_node_id = event_data.get("initial_node_id")
    if not current_node_id:
        # Auto-detect start node
        for n in workflow_raw.get("nodes", []):
            if n.get("type") == "start" or n.get("data", {}).get("node_type") == "start":
                current_node_id = n["id"]
                break
        if not current_node_id and workflow_raw.get("nodes"):
            # fallback to node with no incoming edges
            incoming_targets = {e["target"] for e in edges}
            for n in workflow_raw.get("nodes", []):
                if n["id"] not in incoming_targets:
                    current_node_id = n["id"]
                    break
        if not current_node_id and workflow_raw.get("nodes"):
            current_node_id = workflow_raw["nodes"][0]["id"]

    visited_nodes: List[str] = []
    active_edges: List[str] = []
    trace: List[Dict[str, Any]] = []
    max_steps = 20  # prevent infinite loops
    step_count = 0
    final_decision = None

    try:
        while current_node_id and step_count < max_steps:
            step_count += 1
            node = nodes_map.get(current_node_id)
            if not node:
                break

            visited_nodes.append(current_node_id)
            node_data = node.get("data", {})
            node_type = node.get("type") or node_data.get("node_type", "decision")
            prompt = node_data.get("prompt", node_data.get("label", ""))

            # Handle Start Node
            if node_type == "start":
                # Find outgoing edge from start
                next_edge = next((e for e in edges if e["source"] == current_node_id), None)
                if next_edge:
                    active_edges.append(next_edge["id"])
                    current_node_id = next_edge["target"]
                else:
                    break
                continue

            # Handle End Node
            if node_type == "end":
                final_decision = node_data.get("label", "End")
                break

            # AI Decision Node: Wrap in Inngest step.run for durability & retries
            step_name = f"eval-node-{current_node_id}"

            async def _run_eval(p=prompt, inp=input_text, sys_inst=node_data.get("system_instruction")):
                decision, reasoning, confidence, latency = evaluate_decision_node(
                    prompt=p,
                    input_text=inp,
                    system_instruction=sys_inst,
                )
                return {
                    "decision": decision.value,
                    "reasoning": reasoning,
                    "confidence": confidence,
                    "latency_ms": latency,
                }

            eval_res = await step.run(step_name, _run_eval)
            decision_val = eval_res["decision"]  # "YES" or "NO"
            reasoning_val = eval_res["reasoning"]
            latency_val = eval_res["latency_ms"]

            # Find matching outgoing edge
            handle_match = decision_val.lower()  # "yes" or "no"
            matched_edge = next(
                (e for e in edges if e["source"] == current_node_id and (e.get("sourceHandle") == handle_match or e.get("label", "").lower() == handle_match)),
                None
            )

            next_node_id = matched_edge["target"] if matched_edge else None
            if matched_edge:
                active_edges.append(matched_edge["id"])

            trace_step = {
                "node_id": current_node_id,
                "node_label": node_data.get("label", f"Node {current_node_id}"),
                "prompt": prompt,
                "input_text": input_text,
                "decision": decision_val,
                "reasoning": reasoning_val,
                "confidence": eval_res.get("confidence", 1.0),
                "latency_ms": latency_val,
                "next_node_id": next_node_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            trace.append(trace_step)

            update_run(
                run_id=run_id,
                visited_nodes=visited_nodes,
                active_edges=active_edges,
                trace_step=trace_step,
            )

            final_decision = f"{node_data.get('label')}: {decision_val}"
            current_node_id = next_node_id

        # Completed execution
        update_run(
            run_id=run_id,
            status="completed",
            final_decision=final_decision,
            visited_nodes=visited_nodes,
            active_edges=active_edges,
        )

        return {
            "run_id": run_id,
            "status": "completed",
            "final_decision": final_decision,
            "visited_nodes": visited_nodes,
            "active_edges": active_edges,
            "trace": trace,
        }

    except Exception as e:
        logger.error(f"Workflow execution failed: {e}", exc_info=True)
        update_run(run_id=run_id, status="failed", error=str(e))
        raise


async def trigger_workflow_execution(
    workflow: WorkflowGraph,
    input_text: str,
    initial_node_id: Optional[str] = None,
    background_tasks: Any = None,
) -> Dict[str, Any]:
    """
    Trigger workflow execution returning 202 Accepted instantly.
    Dispatches to Inngest and executes local fallback if in dev mode.
    """
    run_id = f"run_{uuid.uuid4().hex[:10]}"
    create_run(run_id=run_id, status="pending")

    event = inngest.Event(
        name="ai.workflow/run",
        data={
            "run_id": run_id,
            "workflow": workflow.model_dump(),
            "input_text": input_text,
            "initial_node_id": initial_node_id,
        },
    )

    async def _dispatch():
        try:
            await asyncio.wait_for(inngest_client.send(event), timeout=0.25)
        except Exception:
            # Local background worker fallback
            await _run_local_fallback(run_id, workflow, input_text, initial_node_id)

    if background_tasks is not None:
        background_tasks.add_task(_dispatch)
    else:
        asyncio.create_task(_dispatch())

    return {
        "run_id": run_id,
        "status": "pending",
        "status_url": f"/api/workflow/runs/{run_id}",
    }


async def _run_local_fallback(
    run_id: str,
    workflow: WorkflowGraph,
    input_text: str,
    initial_node_id: Optional[str] = None,
):
    """Direct local execution loop for offline or immediate testing."""
    update_run(run_id, status="running")
    nodes_map = {n.id: n for n in workflow.nodes}
    edges = workflow.edges

    current_node_id = initial_node_id
    if not current_node_id:
        for n in workflow.nodes:
            if n.type == "start" or n.data.node_type == "start":
                current_node_id = n.id
                break
        if not current_node_id and workflow.nodes:
            incoming = {e.target for e in edges}
            for n in workflow.nodes:
                if n.id not in incoming:
                    current_node_id = n.id
                    break
        if not current_node_id and workflow.nodes:
            current_node_id = workflow.nodes[0].id

    visited_nodes = []
    active_edges = []
    final_decision = None

    while current_node_id and len(visited_nodes) < 20:
        node = nodes_map.get(current_node_id)
        if not node:
            break

        visited_nodes.append(current_node_id)
        node_type = node.type or node.data.node_type

        if node_type == "start":
            next_edge = next((e for e in edges if e.source == current_node_id), None)
            if next_edge:
                active_edges.append(next_edge.id)
                current_node_id = next_edge.target
            else:
                break
            continue

        if node_type == "end":
            final_decision = node.data.label
            break

        decision, reasoning, confidence, latency = evaluate_decision_node(
            prompt=node.data.prompt or node.data.label,
            input_text=input_text,
            system_instruction=node.data.system_instruction,
        )

        handle_match = decision.value.lower()
        matched_edge = next(
            (e for e in edges if e.source == current_node_id and (e.sourceHandle == handle_match or (e.label or "").lower() == handle_match)),
            None
        )

        next_node_id = matched_edge.target if matched_edge else None
        if matched_edge:
            active_edges.append(matched_edge.id)

        trace_step = {
            "node_id": current_node_id,
            "node_label": node.data.label,
            "prompt": node.data.prompt or node.data.label,
            "input_text": input_text,
            "decision": decision.value,
            "reasoning": reasoning,
            "confidence": confidence,
            "latency_ms": latency,
            "next_node_id": next_node_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        update_run(
            run_id=run_id,
            visited_nodes=visited_nodes,
            active_edges=active_edges,
            trace_step=trace_step,
        )
        final_decision = f"{node.data.label}: {decision.value}"
        current_node_id = next_node_id

    update_run(
        run_id=run_id,
        status="completed",
        final_decision=final_decision,
        visited_nodes=visited_nodes,
        active_edges=active_edges,
    )
