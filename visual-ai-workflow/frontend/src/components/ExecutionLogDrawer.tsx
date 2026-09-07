import React from 'react';
import type { WorkflowRunResult } from '../types';
import { Clock, CheckCircle2, XCircle, Cpu, Zap, Terminal } from 'lucide-react';

interface Props {
  runResult: WorkflowRunResult | null;
  isRunning: boolean;
  onClose: () => void;
}

export const ExecutionLogDrawer: React.FC<Props> = ({ runResult, isRunning }) => {
  if (!runResult && !isRunning) return null;

  return (
    <div className="w-96 bg-[#0f172a]/95 backdrop-blur border-l border-border flex flex-col h-full shadow-2xl z-20">
      {/* Header */}
      <div className="p-4 border-b border-border flex items-center justify-between bg-slate-900/90">
        <div className="flex items-center gap-2">
          <Terminal className="w-5 h-5 text-primary" />
          <h3 className="font-bold text-sm text-slate-100">Execution Inspector</h3>
        </div>
        {isRunning ? (
          <span className="flex items-center gap-1.5 text-xs text-warning bg-warning/10 px-2.5 py-1 rounded-full font-semibold animate-pulse">
            <Cpu className="w-3.5 h-3.5 animate-spin" /> Inngest Running...
          </span>
        ) : runResult?.status === 'completed' ? (
          <span className="flex items-center gap-1.5 text-xs text-success bg-success/15 px-2.5 py-1 rounded-full font-semibold">
            <CheckCircle2 className="w-3.5 h-3.5" /> Completed
          </span>
        ) : (
          <span className="flex items-center gap-1.5 text-xs text-danger bg-danger/15 px-2.5 py-1 rounded-full font-semibold">
            <XCircle className="w-3.5 h-3.5" /> Failed
          </span>
        )}
      </div>

      {/* Meta Info */}
      {runResult && (
        <div className="p-3 bg-slate-950/70 border-b border-border/60 text-xs space-y-1.5 text-slate-400">
          <div className="flex justify-between">
            <span>Run ID:</span>
            <span className="font-mono text-slate-200">{runResult.run_id}</span>
          </div>
          {runResult.final_decision && (
            <div className="flex justify-between font-medium">
              <span>Final Route:</span>
              <span className="text-primary font-bold">{runResult.final_decision}</span>
            </div>
          )}
          <div className="flex justify-between">
            <span>Steps Executed:</span>
            <span className="text-slate-200">{runResult.trace.length} decision node(s)</span>
          </div>
        </div>
      )}

      {/* Trace Step Log List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {runResult?.trace.map((step, idx) => (
          <div
            key={idx}
            className="p-3 rounded-xl bg-slate-900/90 border border-border shadow-sm space-y-2 text-xs"
          >
            {/* Step Header */}
            <div className="flex items-center justify-between">
              <span className="font-bold text-slate-200 flex items-center gap-1.5">
                <span className="w-5 h-5 rounded-full bg-primary/20 text-primary flex items-center justify-center text-[10px]">
                  {idx + 1}
                </span>
                {step.node_label}
              </span>

              <span
                className={`px-2 py-0.5 rounded-md font-extrabold text-[11px] ${
                  step.decision === 'YES'
                    ? 'bg-success/20 text-success border border-success/30'
                    : 'bg-danger/20 text-danger border border-danger/30'
                }`}
              >
                {step.decision}
              </span>
            </div>

            {/* Prompt */}
            <div className="text-[11px] text-slate-400 bg-slate-950/60 p-2 rounded border border-slate-800">
              <span className="font-semibold text-slate-300">Prompt:</span> {step.prompt}
            </div>

            {/* Reasoning */}
            <div className="text-[11px] text-slate-300 leading-relaxed">
              <span className="font-semibold text-primary">AI Reasoning:</span> {step.reasoning}
            </div>

            {/* Footer metrics */}
            <div className="flex items-center justify-between pt-1 border-t border-slate-800/80 text-[10px] text-slate-400 font-mono">
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" /> {step.latency_ms}ms
              </span>
              <span className="flex items-center gap-1">
                <Zap className="w-3 h-3 text-warning" /> Groq Llama-3.3
              </span>
            </div>
          </div>
        ))}

        {runResult?.trace.length === 0 && !isRunning && (
          <div className="text-center text-slate-500 text-xs py-10">
            No execution trace steps yet. Click "Run Workflow" to execute.
          </div>
        )}
      </div>
    </div>
  );
};
