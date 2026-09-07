import type { WorkflowGraph, WorkflowRunResult } from '../types';

export async function executeWorkflowApi(
  workflow: WorkflowGraph,
  inputText: string,
  initialNodeId?: string
): Promise<{ run_id: string; status: string; status_url: string }> {
  const response = await fetch('/api/workflow/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      workflow,
      input_text: inputText,
      initial_node_id: initialNodeId,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(errorData.detail || `Server error: ${response.status}`);
  }

  return response.json();
}

export async function pollRunStatusApi(runId: string): Promise<WorkflowRunResult> {
  const response = await fetch(`/api/workflow/runs/${runId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch run status: ${response.status}`);
  }
  return response.json();
}
