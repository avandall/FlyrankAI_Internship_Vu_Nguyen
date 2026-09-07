"""
Workflow and Node Schema Definitions for Visual AI Workflow System
"""

from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class DecisionType(str, Enum):
    YES = "YES"
    NO = "NO"


class NodeData(BaseModel):
    label: str = Field(default="AI Decision")
    prompt: str = Field(default="", description="Question or criteria for the AI to evaluate")
    node_type: Literal["start", "decision", "end"] = Field(default="decision")
    system_instruction: Optional[str] = None
    status: Literal["idle", "running", "completed", "failed", "skipped"] = Field(default="idle")


class WorkflowNode(BaseModel):
    id: str
    type: Optional[str] = "decision"
    position: Dict[str, float] = Field(default_factory=lambda: {"x": 0.0, "y": 0.0})
    data: NodeData


class WorkflowEdge(BaseModel):
    id: str
    source: str
    target: str
    sourceHandle: Optional[Literal["yes", "no", "start"]] = None
    targetHandle: Optional[str] = None
    label: Optional[str] = None
    animated: Optional[bool] = False


class WorkflowGraph(BaseModel):
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]


class WorkflowExecutionRequest(BaseModel):
    workflow: WorkflowGraph
    input_text: str = Field(..., description="The input context / text to evaluate against the workflow")
    initial_node_id: Optional[str] = Field(default=None, description="Optional start node ID")


class NodeExecutionStep(BaseModel):
    node_id: str
    node_label: str
    prompt: str
    input_text: str
    decision: DecisionType
    reasoning: str
    confidence: Optional[float] = 1.0
    latency_ms: float
    next_node_id: Optional[str] = None
    timestamp: str


class WorkflowExecutionResult(BaseModel):
    run_id: str
    status: Literal["pending", "running", "completed", "failed"]
    final_decision: Optional[str] = None
    visited_nodes: List[str] = Field(default_factory=list)
    active_edges: List[str] = Field(default_factory=list)
    trace: List[NodeExecutionStep] = Field(default_factory=list)
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
