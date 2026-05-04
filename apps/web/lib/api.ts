// API client for Decide platform
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:18000';

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  version: string;
  timestamp: string;
}

export interface Workflow {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'inactive' | 'running';
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  created_at: string;
  updated_at: string;
}

export interface WorkflowNode {
  id: string;
  type: 'agent' | 'memory' | 'tool' | 'decision';
  position: { x: number; y: number };
  data: Record<string, unknown>;
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
}

export interface Log {
  id: string;
  level: 'info' | 'warning' | 'error';
  message: string;
  timestamp: string;
  source?: string;
}

export interface Memory {
  id: string;
  content: string;
  type: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface ExecutionResult {
  id: string;
  workflow_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: string;
  error?: string;
  started_at: string;
  completed_at?: string;
}

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new ApiError(response.status, `API Error: ${response.statusText}`);
  }

  return response.json();
}

// API Functions
export async function getHealth(): Promise<HealthStatus> {
  return fetchApi<HealthStatus>('/api/health');
}

export async function getConfig(): Promise<Record<string, unknown>> {
  return fetchApi<Record<string, unknown>>('/api/config');
}

export async function getWorkflows(): Promise<Workflow[]> {
  try {
    return await fetchApi<Workflow[]>('/api/workflows');
  } catch {
    // Return mock data if API is not available
    return getMockWorkflows();
  }
}

export async function getWorkflow(id: string): Promise<Workflow> {
  try {
    return await fetchApi<Workflow>(`/api/workflows/${id}`);
  } catch {
    const workflows = getMockWorkflows();
    return workflows.find(w => w.id === id) || workflows[0];
  }
}

export async function runWorkflow(id: string): Promise<ExecutionResult> {
  try {
    return await fetchApi<ExecutionResult>(`/api/workflows/${id}/run`, { method: 'POST' });
  } catch {
    // Mock execution result
    return {
      id: `exec-${Date.now()}`,
      workflow_id: id,
      status: 'completed',
      result: 'Workflow executed successfully (mock)',
      started_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
    };
  }
}

export async function saveWorkflow(workflow: Workflow): Promise<Workflow> {
  try {
    return await fetchApi<Workflow>('/api/workflows', {
      method: 'POST',
      body: JSON.stringify(workflow),
    });
  } catch {
    return workflow;
  }
}

export async function getLogs(): Promise<Log[]> {
  try {
    return await fetchApi<Log[]>('/api/logs');
  } catch {
    return getMockLogs();
  }
}

export async function getMemory(): Promise<Memory[]> {
  try {
    return await fetchApi<Memory[]>('/api/memory');
  } catch {
    return getMockMemory();
  }
}

// Mock Data Generators
function getMockWorkflows(): Workflow[] {
  return [
    {
      id: 'wf-1',
      name: 'Customer Support Agent',
      description: 'AI agent for handling customer inquiries',
      status: 'active',
      nodes: [
        { id: 'node-1', type: 'agent', position: { x: 100, y: 100 }, data: { name: 'Support Agent', model: 'gpt-4' } },
        { id: 'node-2', type: 'memory', position: { x: 400, y: 100 }, data: { name: 'Customer Context' } },
        { id: 'node-3', type: 'tool', position: { x: 250, y: 250 }, data: { name: 'Lookup Ticket', tool: 'ticket_db' } },
      ],
      edges: [
        { id: 'edge-1', source: 'node-1', target: 'node-3' },
        { id: 'edge-2', source: 'node-3', target: 'node-2' },
      ],
      created_at: '2024-01-15T10:00:00Z',
      updated_at: '2024-01-20T15:30:00Z',
    },
    {
      id: 'wf-2',
      name: 'Data Analysis Pipeline',
      description: 'Process and analyze incoming data',
      status: 'active',
      nodes: [
        { id: 'node-1', type: 'agent', position: { x: 100, y: 100 }, data: { name: 'Analyzer Agent', model: 'gpt-4' } },
        { id: 'node-2', type: 'decision', position: { x: 400, y: 100 }, data: { name: 'Validate Data', rules: ['non_empty', 'valid_format'] } },
      ],
      edges: [
        { id: 'edge-1', source: 'node-1', target: 'node-2' },
      ],
      created_at: '2024-01-10T08:00:00Z',
      updated_at: '2024-01-18T12:00:00Z',
    },
    {
      id: 'wf-3',
      name: 'Content Generator',
      description: 'Generate marketing content',
      status: 'inactive',
      nodes: [
        { id: 'node-1', type: 'agent', position: { x: 100, y: 100 }, data: { name: 'Content Writer', model: 'gpt-4' } },
      ],
      edges: [],
      created_at: '2024-01-05T09:00:00Z',
      updated_at: '2024-01-05T09:00:00Z',
    },
  ];
}

function getMockLogs(): Log[] {
  return [
    { id: 'log-1', level: 'info', message: 'Workflow customer-support-agent started', timestamp: '2024-01-20T15:30:00Z', source: 'workflow' },
    { id: 'log-2', level: 'info', message: 'Memory context updated', timestamp: '2024-01-20T15:29:00Z', source: 'memory' },
    { id: 'log-3', level: 'warning', message: 'High latency detected on node-2', timestamp: '2024-01-20T15:28:00Z', source: 'performance' },
    { id: 'log-4', level: 'info', message: 'Data pipeline completed', timestamp: '2024-01-20T15:27:00Z', source: 'workflow' },
    { id: 'log-5', level: 'error', message: 'Failed to connect to external API', timestamp: '2024-01-20T15:26:00Z', source: 'api' },
    { id: 'log-6', level: 'info', message: 'Configuration updated', timestamp: '2024-01-20T15:25:00Z', source: 'config' },
    { id: 'log-7', level: 'info', message: 'User session started', timestamp: '2024-01-20T15:24:00Z', source: 'auth' },
    { id: 'log-8', level: 'warning', message: 'Rate limit approaching', timestamp: '2024-01-20T15:23:00Z', source: 'rate_limiter' },
  ];
}

function getMockMemory(): Memory[] {
  return [
    { id: 'mem-1', content: 'User prefers detailed responses', type: 'preference', metadata: { user_id: 'user-1' }, created_at: '2024-01-15T10:00:00Z' },
    { id: 'mem-2', content: 'Last conversation: Product inquiry about enterprise pricing', type: 'conversation', metadata: { user_id: 'user-1', workflow_id: 'wf-1' }, created_at: '2024-01-18T14:30:00Z' },
    { id: 'mem-3', content: 'User prefers email communication', type: 'preference', metadata: { user_id: 'user-2' }, created_at: '2024-01-10T09:00:00Z' },
    { id: 'mem-4', content: 'FAQ: How to reset password', type: 'faq', metadata: { category: 'account' }, created_at: '2024-01-05T08:00:00Z' },
    { id: 'mem-5', content: 'Known issue: API timeout under heavy load', type: 'knowledge', metadata: { severity: 'known' }, created_at: '2024-01-01T12:00:00Z' },
  ];
}

export const api = {
  getHealth,
  getConfig,
  getWorkflows,
  getWorkflow,
  runWorkflow,
  saveWorkflow,
  getLogs,
  getMemory,
};