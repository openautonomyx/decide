import { create } from 'zustand';
import { Workflow, WorkflowNode, WorkflowEdge } from './api';

interface BuilderState {
  currentWorkflow: Workflow | null;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  selectedNode: string | null;
  isDirty: boolean;
  setCurrentWorkflow: (workflow: Workflow | null) => void;
  setNodes: (nodes: WorkflowNode[]) => void;
  setEdges: (edges: WorkflowEdge[]) => void;
  addNode: (node: WorkflowNode) => void;
  updateNode: (id: string, data: Partial<WorkflowNode['data']>) => void;
  removeNode: (id: string) => void;
  addEdge: (edge: WorkflowEdge) => void;
  removeEdge: (id: string) => void;
  setSelectedNode: (id: string | null) => void;
  setDirty: (dirty: boolean) => void;
  reset: () => void;
}

export const useBuilderStore = create<BuilderState>((set) => ({
  currentWorkflow: null,
  nodes: [],
  edges: [],
  selectedNode: null,
  isDirty: false,

  setCurrentWorkflow: (workflow) => set({ 
    currentWorkflow: workflow,
    nodes: workflow?.nodes || [],
    edges: workflow?.edges || [],
    isDirty: false,
  }),

  setNodes: (nodes) => set({ nodes, isDirty: true }),
  setEdges: (edges) => set({ edges, isDirty: true }),

  addNode: (node) => set((state) => ({ 
    nodes: [...state.nodes, node],
    isDirty: true,
  })),

  updateNode: (id, data) => set((state) => ({
    nodes: state.nodes.map((n) => 
      n.id === id ? { ...n, data: { ...n.data, ...data } } : n
    ),
    isDirty: true,
  })),

  removeNode: (id) => set((state) => ({ 
    nodes: state.nodes.filter((n) => n.id !== id),
    edges: state.edges.filter((e) => e.source !== id && e.target !== id),
    selectedNode: state.selectedNode === id ? null : state.selectedNode,
    isDirty: true,
  })),

  addEdge: (edge) => set((state) => ({ 
    edges: [...state.edges, edge],
    isDirty: true,
  })),

  removeEdge: (id) => set((state) => ({ 
    edges: state.edges.filter((e) => e.id !== id),
    isDirty: true,
  })),

  setSelectedNode: (id) => set({ selectedNode: id }),
  setDirty: (dirty) => set({ isDirty: dirty }),
  reset: () => set({ 
    currentWorkflow: null,
    nodes: [],
    edges: [],
    selectedNode: null,
    isDirty: false,
  }),
}));

interface UIState {
  sidebarOpen: boolean;
  rightPanelOpen: boolean;
  activeTab: string;
  toggleSidebar: () => void;
  toggleRightPanel: () => void;
  setActiveTab: (tab: string) => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  rightPanelOpen: true,
  activeTab: 'dashboard',
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  toggleRightPanel: () => set((state) => ({ rightPanelOpen: !state.rightPanelOpen })),
  setActiveTab: (tab) => set({ activeTab: tab }),
}));

interface AppState {
  messages: Message[];
  isProcessing: boolean;
  currentWorkflowId: string | null;
  addMessage: (message: Message) => void;
  updateLastMessage: (content: string) => void;
  setProcessing: (processing: boolean) => void;
  setWorkflowId: (id: string | null) => void;
  clearMessages: () => void;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export const useAppStore = create<AppState>((set) => ({
  messages: [],
  isProcessing: false,
  currentWorkflowId: null,

  addMessage: (message) => set((state) => ({ 
    messages: [...state.messages, message],
  })),

  updateLastMessage: (content) => set((state) => ({
    messages: state.messages.map((m, i) => 
      i === state.messages.length - 1 ? { ...m, content } : m
    ),
  })),

  setProcessing: (processing) => set({ isProcessing: processing }),
  setWorkflowId: (id) => set({ currentWorkflowId: id }),
  clearMessages: () => set({ messages: [] }),
}));