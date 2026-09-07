import type { Node, Edge } from '@xyflow/react';

export type DecisionValue = "YES" | "NO";

export interface NodeData extends Record<string, unknown> {
  label: string;
  prompt: string;
  node_type?: "start" | "decision" | "end";
  status?: "idle" | "running" | "completed" | "failed" | "skipped";
  lastDecision?: DecisionValue;
  lastReasoning?: string;
  onChangePrompt?: (prompt: string) => void;
  onChangeLabel?: (label: string) => void;
  onDelete?: () => void;
}

export type CustomNode = Node<NodeData>;

export interface NodeExecutionStep {
  node_id: string;
  node_label: string;
  prompt: string;
  input_text: string;
  decision: DecisionValue;
  reasoning: string;
  confidence: number;
  latency_ms: number;
  next_node_id?: string;
  timestamp: string;
}

export interface WorkflowRunResult {
  run_id: string;
  status: "pending" | "running" | "completed" | "failed";
  final_decision?: string;
  visited_nodes: string[];
  active_edges: string[];
  trace: NodeExecutionStep[];
  error?: string;
  created_at: string;
  completed_at?: string;
}

export interface WorkflowGraph {
  nodes: CustomNode[];
  edges: Edge[];
}
