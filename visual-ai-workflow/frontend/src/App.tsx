import React, { useState, useCallback, useEffect } from 'react';
import {
  ReactFlow,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  BackgroundVariant,
} from '@xyflow/react';
import type { Connection, Edge, NodeTypes } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { DecisionNode } from './components/DecisionNode';
import { StartNode, EndNode } from './components/StartEndNode';
import { WorkflowToolbar } from './components/WorkflowToolbar';
import { ExecutionLogDrawer } from './components/ExecutionLogDrawer';
import { PRESETS } from './lib/presets';
import { executeWorkflowApi, pollRunStatusApi } from './lib/api';
import type { CustomNode, NodeData, WorkflowRunResult } from './types';

const nodeTypes: NodeTypes = {
  decision: DecisionNode as any,
  start: StartNode as any,
  end: EndNode as any,
};

export default function App() {
  const [inputText, setInputText] = useState(PRESETS[0].defaultInput);
  const [isRunning, setIsRunning] = useState(false);
  const [runResult, setRunResult] = useState<WorkflowRunResult | null>(null);

  // React Flow State
  const [nodes, setNodes, onNodesChange] = useNodesState<CustomNode>(PRESETS[0].nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(PRESETS[0].edges);

  // Hook prompt & label editing into nodes
  const bindNodeCallbacks = useCallback((rawNodes: CustomNode[]): CustomNode[] => {
    return rawNodes.map((n) => ({
      ...n,
      data: {
        ...n.data,
        onChangePrompt: (newPrompt: string) => {
          setNodes((nds) =>
            nds.map((node) =>
              node.id === n.id ? { ...node, data: { ...node.data, prompt: newPrompt } } : node
            )
          );
        },
        onChangeLabel: (newLabel: string) => {
          setNodes((nds) =>
            nds.map((node) =>
              node.id === n.id ? { ...node, data: { ...node.data, label: newLabel } } : node
            )
          );
        },
        onDelete: () => {
          setNodes((nds) => nds.filter((node) => node.id !== n.id));
          setEdges((eds) => eds.filter((edge) => edge.source !== n.id && edge.target !== n.id));
        },
      },
    }));
  }, [setNodes, setEdges]);

  // Load preset
  const handleSelectPreset = (presetId: string) => {
    const preset = PRESETS.find((p) => p.id === presetId) || PRESETS[0];
    setInputText(preset.defaultInput);
    setRunResult(null);
    setNodes(bindNodeCallbacks(preset.nodes));
    setEdges(preset.edges);
  };

  useEffect(() => {
    setNodes(bindNodeCallbacks(PRESETS[0].nodes));
  }, []);

  // Connect edges
  const onConnect = useCallback(
    (params: Connection) => {
      const isYes = params.sourceHandle === 'yes';
      const isNo = params.sourceHandle === 'no';
      const newEdge: Edge = {
        ...params,
        id: `e-${params.source}-${params.target}-${Date.now()}`,
        type: 'smoothstep',
        label: isYes ? 'YES' : isNo ? 'NO' : undefined,
        style: {
          stroke: isYes ? '#10b981' : isNo ? '#ef4444' : '#64748b',
          strokeWidth: 2,
        },
      };
      setEdges((eds) => addEdge(newEdge, eds));
    },
    [setEdges]
  );

  // Add Decision Node
  const handleAddDecisionNode = () => {
    const id = `node-${Date.now()}`;
    const newNode: CustomNode = {
      id,
      type: 'decision',
      position: { x: 250 + Math.random() * 80, y: 250 + Math.random() * 80 },
      data: {
        label: 'New AI Decision',
        prompt: 'Does this meet the criteria? (YES or NO)',
        node_type: 'decision',
        status: 'idle',
      },
    };
    setNodes((nds) => [...nds, ...bindNodeCallbacks([newNode])]);
  };

  // Add End Node
  const handleAddEndNode = () => {
    const id = `end-${Date.now()}`;
    const newNode: CustomNode = {
      id,
      type: 'end',
      position: { x: 300 + Math.random() * 60, y: 480 + Math.random() * 60 },
      data: {
        label: 'New Outcome Action',
        prompt: '',
        node_type: 'end',
        status: 'idle',
      },
    };
    setNodes((nds) => [...nds, ...bindNodeCallbacks([newNode])]);
  };

  // Export JSON
  const handleExportJson = () => {
    const workflow = { nodes, edges, defaultInput: inputText };
    const blob = new Blob([JSON.stringify(workflow, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ai_workflow_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Import JSON
  const handleImportJson = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const parsed = JSON.parse(event.target?.result as string);
        if (parsed.nodes && parsed.edges) {
          setNodes(bindNodeCallbacks(parsed.nodes));
          setEdges(parsed.edges);
          if (parsed.defaultInput) setInputText(parsed.defaultInput);
          setRunResult(null);
        }
      } catch (err) {
        alert('Invalid workflow JSON file format.');
      }
    };
    reader.readAsText(file);
  };

  // RUN WORKFLOW
  const handleRunWorkflow = async () => {
    if (!inputText.trim()) {
      alert('Please enter an input context text to evaluate.');
      return;
    }

    setIsRunning(true);
    setRunResult(null);

    // Reset node status to idle
    setNodes((nds) =>
      nds.map((n) => ({
        ...n,
        data: { ...n.data, status: 'idle', lastDecision: undefined, lastReasoning: undefined },
      }))
    );
    setEdges((eds) => eds.map((e) => ({ ...e, animated: false })));

    try {
      const graphData = {
        nodes: nodes.map((n) => ({
          id: n.id,
          type: n.type || 'decision',
          position: n.position,
          data: {
            label: n.data.label,
            prompt: n.data.prompt,
            node_type: n.data.node_type || 'decision',
          },
        })),
        edges: edges.map((e) => ({
          id: e.id,
          source: e.source,
          target: e.target,
          sourceHandle: e.sourceHandle as any,
          targetHandle: e.targetHandle as any,
          label: e.label as string,
        })),
      };

      const startResp = await executeWorkflowApi(graphData as any, inputText);
      const runId = startResp.run_id;

      // Poll run status
      let attempts = 0;
      const pollInterval = setInterval(async () => {
        attempts++;
        try {
          const statusResult = await pollRunStatusApi(runId);
          setRunResult(statusResult);

          // Update active nodes & animated edges
          const visitedSet = new Set(statusResult.visited_nodes);
          const activeEdgeSet = new Set(statusResult.active_edges);
          const traceMap = new Map(statusResult.trace.map((t) => [t.node_id, t]));

          setNodes((nds) =>
            nds.map((n) => {
              const traceStep = traceMap.get(n.id);
              const isVisited = visitedSet.has(n.id);
              let status: NodeData['status'] = 'idle';

              if (statusResult.status === 'running' && isVisited) {
                status = 'running';
              } else if (isVisited) {
                status = 'completed';
              } else if (statusResult.status === 'completed') {
                status = 'skipped';
              }

              return {
                ...n,
                data: {
                  ...n.data,
                  status,
                  lastDecision: traceStep?.decision,
                  lastReasoning: traceStep?.reasoning,
                },
              };
            })
          );

          setEdges((eds) =>
            eds.map((e) => ({
              ...e,
              animated: activeEdgeSet.has(e.id),
              style: activeEdgeSet.has(e.id)
                ? { ...e.style, strokeWidth: 3, filter: 'drop-shadow(0 0 6px rgba(59, 130, 246, 0.8))' }
                : e.style,
            }))
          );

          if (statusResult.status === 'completed' || statusResult.status === 'failed' || attempts > 25) {
            clearInterval(pollInterval);
            setIsRunning(false);
          }
        } catch (err) {
          clearInterval(pollInterval);
          setIsRunning(false);
        }
      }, 350);
    } catch (err: any) {
      alert(`Execution Error: ${err.message}`);
      setIsRunning(false);
    }
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-background">
      {/* Top Toolbar */}
      <WorkflowToolbar
        onAddDecisionNode={handleAddDecisionNode}
        onAddEndNode={handleAddEndNode}
        onSelectPreset={handleSelectPreset}
        onExportJson={handleExportJson}
        onImportJson={handleImportJson}
        onRunWorkflow={handleRunWorkflow}
        isRunning={isRunning}
        inputText={inputText}
        setInputText={setInputText}
      />

      {/* Main Content Area */}
      <div className="flex flex-1 h-[calc(100vh-60px)] relative">
        {/* React Flow Canvas */}
        <div className="flex-1 h-full relative">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            nodeTypes={nodeTypes}
            fitView
            minZoom={0.2}
            maxZoom={1.8}
            className="bg-[#090d16]"
          >
            <Background variant={BackgroundVariant.Dots} gap={20} size={1.2} color="#1e293b" />
            <Controls className="!bg-slate-900 !border-slate-800 !text-slate-200" />
            <MiniMap
              nodeStrokeColor="#3b82f6"
              nodeColor="#1e293b"
              className="!bg-slate-950/80 !border !border-slate-800 !rounded-lg"
            />
          </ReactFlow>
        </div>

        {/* Right Execution Inspector Drawer */}
        <ExecutionLogDrawer
          runResult={runResult}
          isRunning={isRunning}
          onClose={() => setRunResult(null)}
        />
      </div>
    </div>
  );
}
