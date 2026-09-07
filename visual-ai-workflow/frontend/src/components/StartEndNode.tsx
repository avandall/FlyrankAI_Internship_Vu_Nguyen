import { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import type { NodeProps } from '@xyflow/react';
import type { CustomNode } from '../types';
import { PlayCircle, Flag } from 'lucide-react';

export const StartNode = memo(({ data, isConnectable }: NodeProps<CustomNode>) => {
  const isRunning = data.status === 'running';
  const isCompleted = data.status === 'completed';

  return (
    <div className={`px-5 py-3 rounded-xl bg-gradient-to-r from-blue-900/90 to-indigo-950/90 border-2 ${isRunning ? 'border-warning running-node-glow' : isCompleted ? 'border-success' : 'border-blue-500'} shadow-xl text-white flex items-center gap-3`}>
      <PlayCircle className="w-5 h-5 text-blue-400" />
      <div>
        <div className="text-[10px] uppercase font-extrabold tracking-widest text-blue-300">START EVENT</div>
        <div className="text-xs font-bold">{data.label || 'Workflow Entry'}</div>
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        isConnectable={isConnectable}
        className="!w-4 !h-4 !bg-blue-400 !border-2 !border-background"
      />
    </div>
  );
});
StartNode.displayName = 'StartNode';

export const EndNode = memo(({ data, isConnectable }: NodeProps<CustomNode>) => {
  const isVisited = data.status === 'completed';

  return (
    <div className={`px-5 py-3 rounded-xl bg-gradient-to-r from-slate-900 to-slate-950 border-2 ${isVisited ? 'border-success ring-2 ring-success/40 bg-emerald-950/40' : 'border-slate-700'} shadow-xl text-white flex items-center gap-3`}>
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
        className="!w-4 !h-4 !bg-emerald-400 !border-2 !border-background"
      />
      <Flag className={`w-5 h-5 ${isVisited ? 'text-success' : 'text-slate-400'}`} />
      <div>
        <div className="text-[10px] uppercase font-extrabold tracking-widest text-slate-400">OUTCOME</div>
        <div className="text-xs font-bold text-slate-100">{data.label || 'Workflow End'}</div>
      </div>
    </div>
  );
});
EndNode.displayName = 'EndNode';
