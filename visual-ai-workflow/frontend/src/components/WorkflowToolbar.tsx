import React from 'react';
import { PRESETS } from '../lib/presets';
import {
  Play,
  PlusCircle,
  Download,
  Upload,
  RefreshCw,
  FolderOpen,
  Sparkles,
} from 'lucide-react';

interface Props {
  onAddDecisionNode: () => void;
  onAddEndNode: () => void;
  onSelectPreset: (presetId: string) => void;
  onExportJson: () => void;
  onImportJson: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onRunWorkflow: () => void;
  isRunning: boolean;
  inputText: string;
  setInputText: (text: string) => void;
}

export const WorkflowToolbar: React.FC<Props> = ({
  onAddDecisionNode,
  onAddEndNode,
  onSelectPreset,
  onExportJson,
  onImportJson,
  onRunWorkflow,
  isRunning,
  inputText,
  setInputText,
}) => {
  return (
    <div className="bg-[#0b1120]/95 backdrop-blur border-b border-border px-4 py-2.5 flex flex-wrap items-center justify-between gap-3 shadow-lg z-10">
      {/* Brand & Presets */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-primary to-indigo-500 flex items-center justify-center shadow-md">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <div>
            <h1 className="font-extrabold text-sm text-slate-100 tracking-tight">Visual AI Workflow</h1>
            <p className="text-[10px] text-slate-400">Inngest + React Flow + Groq LLM</p>
          </div>
        </div>

        <div className="h-6 w-px bg-border mx-1 hidden md:block" />

        {/* Preset selector */}
        <div className="flex items-center gap-1.5">
          <FolderOpen className="w-3.5 h-3.5 text-slate-400" />
          <select
            onChange={(e) => onSelectPreset(e.target.value)}
            className="text-xs bg-slate-900 border border-slate-700 text-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-primary"
            defaultValue="support-triage"
          >
            {PRESETS.map((p) => (
              <option key={p.id} value={p.id}>
                Template: {p.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Input Context box */}
      <div className="flex-1 max-w-xl min-w-[280px]">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Enter input context to evaluate (e.g. ticket message, inquiry, text)..."
          className="w-full text-xs bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary shadow-inner"
        />
      </div>

      {/* Action buttons */}
      <div className="flex items-center gap-2">
        <button
          onClick={onAddDecisionNode}
          className="flex items-center gap-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 px-2.5 py-1.5 rounded-lg font-medium transition-colors"
          title="Add new AI Decision Node"
        >
          <PlusCircle className="w-3.5 h-3.5 text-primary" />
          <span>+ Decision</span>
        </button>

        <button
          onClick={onAddEndNode}
          className="flex items-center gap-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 px-2.5 py-1.5 rounded-lg font-medium transition-colors"
          title="Add Outcome / End Node"
        >
          <PlusCircle className="w-3.5 h-3.5 text-emerald-400" />
          <span>+ Outcome</span>
        </button>

        <button
          onClick={onExportJson}
          className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 rounded-lg transition-colors"
          title="Export Workflow JSON"
        >
          <Download className="w-4 h-4" />
        </button>

        <label
          className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 rounded-lg cursor-pointer transition-colors"
          title="Import Workflow JSON"
        >
          <Upload className="w-4 h-4" />
          <input type="file" accept=".json" onChange={onImportJson} className="hidden" />
        </label>

        {/* Primary Run button */}
        <button
          onClick={onRunWorkflow}
          disabled={isRunning}
          className={`flex items-center gap-1.5 text-xs px-4 py-1.5 rounded-lg font-bold shadow-md transition-all ${
            isRunning
              ? 'bg-warning/80 text-black cursor-not-allowed'
              : 'bg-primary hover:bg-primary-hover text-white hover:shadow-primary/25 hover:shadow-lg'
          }`}
        >
          {isRunning ? (
            <>
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              <span>Running...</span>
            </>
          ) : (
            <>
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Run Workflow</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};
