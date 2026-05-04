'use client';

import { Handle, Position, NodeProps } from '@xyflow/react';
import { Bot, Database, Wrench, GitBranch } from 'lucide-react';

export function AgentNode({ data }: NodeProps) {
  return (
    <div className="rounded-lg border-2 border-blue-500 bg-background px-4 py-3 shadow-lg min-w-[150px]">
      <Handle type="target" position={Position.Top} className="!bg-blue-500" />
      <div className="flex items-center gap-2">
        <Bot className="h-5 w-5 text-blue-500" />
        <div>
          <div className="text-sm font-medium">{data.label as string}</div>
          <div className="text-xs text-muted-foreground">
            {(data.model as string) || 'gpt-4'}
          </div>
        </div>
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-blue-500" />
    </div>
  );
}

export function MemoryNode({ data }: NodeProps) {
  return (
    <div className="rounded-lg border-2 border-purple-500 bg-background px-4 py-3 shadow-lg min-w-[150px]">
      <Handle type="target" position={Position.Top} className="!bg-purple-500" />
      <div className="flex items-center gap-2">
        <Database className="h-5 w-5 text-purple-500" />
        <div>
          <div className="text-sm font-medium">{data.label as string}</div>
          <div className="text-xs text-muted-foreground">Memory</div>
        </div>
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-purple-500" />
    </div>
  );
}

export function ToolNode({ data }: NodeProps) {
  return (
    <div className="rounded-lg border-2 border-green-500 bg-background px-4 py-3 shadow-lg min-w-[150px]">
      <Handle type="target" position={Position.Top} className="!bg-green-500" />
      <div className="flex items-center gap-2">
        <Wrench className="h-5 w-5 text-green-500" />
        <div>
          <div className="text-sm font-medium">{data.label as string}</div>
          <div className="text-xs text-muted-foreground">
            {(data.tool as string) || 'tool'}
          </div>
        </div>
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-green-500" />
    </div>
  );
}

export function DecisionNode({ data }: NodeProps) {
  return (
    <div className="rounded-lg border-2 border-orange-500 bg-background px-4 py-3 shadow-lg min-w-[150px]">
      <Handle type="target" position={Position.Top} className="!bg-orange-500" />
      <div className="flex items-center gap-2">
        <GitBranch className="h-5 w-5 text-orange-500" />
        <div>
          <div className="text-sm font-medium">{data.label as string}</div>
          <div className="text-xs text-muted-foreground">Decision</div>
        </div>
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-orange-500" />
    </div>
  );
}