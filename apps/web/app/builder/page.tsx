'use client';

import { useCallback, useState } from 'react';
import {
  ReactFlow,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Node,
  BackgroundVariant,
  Panel,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  AgentNode,
  MemoryNode,
  ToolNode,
  DecisionNode,
} from './nodes';
import { Play, Save, Plus, Trash2, Download, Upload } from 'lucide-react';
import { useWorkflows, useRunWorkflow, useSaveWorkflow } from '@/lib/hooks';
import { useBuilderStore } from '@/lib/store';
import { useRouter } from 'next/navigation';

const nodeTypes = {
  agent: AgentNode,
  memory: MemoryNode,
  tool: ToolNode,
  decision: DecisionNode,
};

const initialNodes: Node[] = [
  {
    id: '1',
    type: 'agent',
    position: { x: 100, y: 100 },
    data: { label: 'Agent Node', model: 'gpt-4' },
  },
];

export default function BuilderPage() {
  const router = useRouter();
  const { data: workflows } = useWorkflows();
  const runWorkflow = useRunWorkflow();
  const saveWorkflow = useSaveWorkflow();
  const { isDirty } = useBuilderStore();

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<string>('');

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedNodeId(node.id);
  }, []);

  const addNode = (type: string) => {
    const newNode: Node = {
      id: `${Date.now()}`,
      type,
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      data: { label: `${type.charAt(0).toUpperCase() + type.slice(1)} Node` },
    };
    setNodes((nds) => [...nds, newNode]);
  };

  const deleteNode = () => {
    if (selectedNodeId) {
      setNodes((nds) => nds.filter((n) => n.id !== selectedNodeId));
      setEdges((eds) =>
        eds.filter((e: Edge) => e.source !== selectedNodeId && e.target !== selectedNodeId)
      );
      setSelectedNodeId(null);
    }
  };

  const handleRun = async () => {
    const workflowData = {
      id: selectedWorkflowId || `wf-${Date.now()}`,
      name: 'Workflow',
      description: 'Created in builder',
      status: 'active' as const,
      nodes: nodes.map((n) => ({
        id: n.id,
        type: n.type as 'agent' | 'memory' | 'tool' | 'decision',
        position: n.position,
        data: n.data,
      })),
      edges: edges.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
      })),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    await runWorkflow.mutateAsync(workflowData.id);
    router.push('/workflows');
  };

  const handleSave = () => {
    const workflowData = {
      id: selectedWorkflowId || `wf-${Date.now()}`,
      name: 'Workflow',
      description: 'Created in builder',
      status: 'active' as const,
      nodes: nodes.map((n) => ({
        id: n.id,
        type: n.type as 'agent' | 'memory' | 'tool' | 'decision',
        position: n.position,
        data: n.data,
      })),
      edges: edges.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
      })),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    saveWorkflow.mutate(workflowData);
  };

  const exportWorkflow = () => {
    const data = JSON.stringify({ nodes, edges }, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'workflow.json';
    a.click();
  };

  const selectedNode = nodes.find((n) => n.id === selectedNodeId);

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4">
      {/* Main Builder */}
      <div className="flex-1 rounded-lg border bg-background overflow-hidden">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
        >
          <Controls />
          <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
          
          <Panel position="top-left" className="flex gap-2">
            <Select onValueChange={(v) => addNode(v)}>
              <SelectTrigger className="w-40">
                <Plus className="mr-2 h-4 w-4" />
                <SelectValue placeholder="Add Node" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="agent">Agent</SelectItem>
                <SelectItem value="memory">Memory</SelectItem>
                <SelectItem value="tool">Tool</SelectItem>
                <SelectItem value="decision">Decision</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" size="sm" onClick={deleteNode} disabled={!selectedNodeId}>
              <Trash2 className="mr-1 h-3 w-3" />
              Delete
            </Button>
          </Panel>

          <Panel position="top-right" className="flex gap-2">
            <Button variant="outline" size="sm" onClick={exportWorkflow}>
              <Download className="mr-1 h-3 w-3" />
              Export
            </Button>
            <Button variant="outline" size="sm" onClick={handleSave} disabled={!isDirty}>
              <Save className="mr-1 h-3 w-3" />
              Save
            </Button>
            <Button size="sm" onClick={handleRun}>
              <Play className="mr-1 h-3 w-3" />
              Run
            </Button>
          </Panel>
        </ReactFlow>
      </div>

      {/* Right Panel - Node Config */}
      <Card className="w-80">
        <CardHeader>
          <CardTitle>Node Configuration</CardTitle>
          <CardDescription>
            {selectedNode ? 'Edit selected node' : 'Select a node to edit'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {selectedNode ? (
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium">Label</label>
                <Input
                  value={selectedNode.data.label as string}
                  onChange={(e) => {
                    setNodes((nds) =>
                      nds.map((n) =>
                        n.id === selectedNodeId
                          ? { ...n, data: { ...n.data, label: e.target.value } }
                          : n
                      )
                    );
                  }}
                />
              </div>
              <div>
                <label className="text-sm font-medium">Type</label>
                <Badge variant="secondary" className="mt-1 block">
                  {selectedNode.type}
                </Badge>
              </div>
              {selectedNode.type === 'agent' && (
                <div>
                  <label className="text-sm font-medium">Model</label>
                  <Select
                    value={(selectedNode.data.model as string) || 'gpt-4'}
                    onValueChange={(v) => {
                      setNodes((nds) =>
                        nds.map((n) =>
                          n.id === selectedNodeId
                            ? { ...n, data: { ...n.data, model: v } }
                            : n
                        )
                      );
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="gpt-4">GPT-4</SelectItem>
                      <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                      <SelectItem value="claude-3">Claude 3</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center text-muted-foreground py-8">
              <p>Click on a node to edit its properties</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}