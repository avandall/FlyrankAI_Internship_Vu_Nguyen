import { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import type { NodeProps } from '@xyflow/react';
import type { CustomNode } from '../types';
import { Bot, CheckCircle2, XCircle, Trash2, Cpu, Sparkles } from 'lucide-react';

export const DecisionNode = memo(({ data, isConnectable }: NodeProps<CustomNode>) => {
  const status = data.status || 'idle';

  let statusBorder = 'border-border hover:border-slate-500';
  let statusBadge = null;

  if (status === 'running') {
    statusBorder = 'border-warning running-node-glow ring-2 ring-warning/50';
    statusBadge = (
      <span className="flex items-center gap-1 text-[11px] font-semibold text-warning bg-warning/10 px-2 py-0.5 rounded-full animate-pulse">
        <Cpu className="w-3 h-3 animate-spin" /> Evaluating...
      </span>
    );
  } else if (status === 'completed') {
    statusBorder = 'border-success ring-2 ring-success/30';
    statusBadge = (
      <span className="flex items-center gap-1 text-[11px] font-bold text-success bg-success/15 px-2 py-0.5 rounded-full">
        <CheckCircle2 className="w-3 h-3" /> Result: {data.lastDecision || 'DONE'}
      </span>
    );
  } else if (status === 'failed') {
    statusBorder = 'border-danger ring-2 ring-danger/30';
    statusBadge = (
      <span className="flex items-center gap-1 text-[11px] font-bold text-danger bg-danger/15 px-2 py-0.5 rounded-full">
        <XCircle className="w-3 h-3" /> Failed
      </span>
    );
  } else if (status === 'skipped') {
    statusBorder = 'border-slate-800 opacity-40';
  }

  return (
    <div className={`w-80 rounded-xl bg-[#111827]/95 backdrop-blur border-2 ${statusBorder} shadow-2xl transition-all duration-200 text-slate-100 overflow-hidden`}>
      {/* Target Handle (Top) */}
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
        className="!w-4 !h-4 !bg-primary !border-2 !border-background hover:!scale-125 transition-transform"
      />

      {/* Header */}
      <div className="flex items-center justify-between px-3.5 py-2.5 bg-slate-900/90 border-b border-border">
        <div className="flex items-center gap-2 flex-1 mr-2">
          <div className="p-1.5 rounded-lg bg-primary/20 text-primary">
            <Bot className="w-4 h-4" />
          </div>
          <input
            type="text"
            value={data.label || ''}
            onChange={(e) => data.onChangeLabel?.(e.target.value)}
            className="bg-transparent font-bold text-sm tracking-wide text-slate-100 focus:outline-none focus:ring-1 focus:ring-primary rounded px-1 w-full"
            placeholder="Node Label"
          />
        </div>

        {data.onDelete && (
          <button
            onClick={data.onDelete}
            title="Delete Node"
            className="p-1 text-slate-400 hover:text-danger hover:bg-danger/10 rounded transition-colors"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Body: Prompt input */}
      <div className="p-3.5 space-y-2.5">
        <div className="flex items-center justify-between">
          <label className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-primary" /> AI Evaluation Prompt
          </label>
          {statusBadge}
        </div>

        <textarea
          rows={3}
          value={data.prompt || ''}
          onChange={(e) => data.onChangePrompt?.(e.target.value)}
          placeholder="e.g. Is this an urgent customer support inquiry? (Returns YES or NO)"
          className="w-full text-xs p-2.5 bg-slate-950/80 border border-slate-700/80 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all resize-none leading-relaxed"
        />

        {data.lastReasoning && (
          <div className="p-2 rounded bg-slate-900/80 border border-slate-800 text-[11px] text-slate-300 italic">
            💡 <span className="font-semibold text-slate-400">Reasoning:</span> {data.lastReasoning}
          </div>
        )}
      </div>

      {/* Bottom Branch Handles: YES & NO */}
      <div className="grid grid-cols-2 border-t border-border bg-slate-900/60 p-2.5 text-xs font-bold">
        {/* YES Handle */}
        <div className="flex items-center justify-start gap-1.5 pl-1 text-success relative">
          <span className="w-2 h-2 rounded-full bg-success"></span>
          <span>YES Branch</span>
          <Handle
            id="yes"
            type="source"
            position={Position.Bottom}
            style={{ left: '25%' }}
            isConnectable={isConnectable}
            className="!w-4 !h-4 !bg-success !border-2 !border-background hover:!scale-125 transition-transform"
          />
        </div>

        {/* NO Handle */}
        <div className="flex items-center justify-end gap-1.5 pr-1 text-danger relative">
          <span>NO Branch</span>
          <span className="w-2 h-2 rounded-full bg-danger"></span>
          <Handle
            id="no"
            type="source"
            position={Position.Bottom}
            style={{ left: '75%' }}
            isConnectable={isConnectable}
            className="!w-4 !h-4 !bg-danger !border-2 !border-background hover:!scale-125 transition-transform"
          />
        </div>
      </div>
    </div>
  );
});
DecisionNode.displayName = 'DecisionNode';
