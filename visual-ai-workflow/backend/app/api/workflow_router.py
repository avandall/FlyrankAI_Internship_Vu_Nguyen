"""
Workflow APIRouter for triggering runs and polling execution status
"""

from typing import Any, Dict, List
from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from app.models.workflow_schema import WorkflowExecutionRequest, WorkflowGraph
from app.services.inngest_workflow_service import trigger_workflow_execution
from app.storage.run_store import get_run, list_runs

router = APIRouter(prefix="/api/workflow", tags=["AI Workflow Engine"])


@router.post(
    "/execute",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Execute Visual AI Workflow",
)
async def execute_workflow(
    request: WorkflowExecutionRequest,
    background_tasks: BackgroundTasks,
) -> Dict[str, Any]:
    """
    Accepts workflow graph and input context, triggers Inngest workflow and returns 202 Accepted.
    """
    if not request.workflow.nodes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow must contain at least one node.",
        )
    if not request.input_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="input_text cannot be empty.",
        )

    result = await trigger_workflow_execution(
        workflow=request.workflow,
        input_text=request.input_text,
        initial_node_id=request.initial_node_id,
        background_tasks=background_tasks,
    )
    return result


@router.get(
    "/runs/{run_id}",
    summary="Get Workflow Run Status & Trace",
)
def get_workflow_run_status(run_id: str) -> Dict[str, Any]:
    """Poll run status, current active node, visited path, and detailed LLM reasoning trace."""
    record = get_run(run_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run '{run_id}' not found.",
        )
    return record


@router.get(
    "/runs",
    summary="List all workflow runs",
)
def list_workflow_runs() -> List[Dict[str, Any]]:
    return list_runs()
