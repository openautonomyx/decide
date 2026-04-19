# LangGraph → LangFlow Compiler

This compiler translates LangGraph-style workflow definitions into LangFlow-compatible flow structures that can be imported, visualized, edited, and exported back into Decide.

## Overview

The compiler is a translation layer that preserves metadata, tools, skills, memory bindings, and approval/governance constructs when converting between frameworks.

## Supported Mappings

### Basic Graph Structure

| LangGraph | LangFlow | Description |
|----------|---------|-------------|
| `start` | Start | Workflow start |
| `end` / `END` | End | Workflow end |

### Execution Nodes

| LangGraph | LangFlow | Description |
|----------|---------|-------------|
| `llm` | OpenAI | LLM execution |
| `tool` | Tool | Tool execution |
| `prompt` | Prompt | Prompt template |
| `transform` | Function | Transform/function |
| `condition` | DecisionGate | Conditional routing |
| `decision` | DecisionGate | Decision/gate |

### Context/Governance Nodes

| LangGraph | LangFlow | Description |
|----------|---------|-------------|
| `approval` | ApprovalGate | Approval checkpoint |
| `memory` | MemoryRecall | Memory fetch/injection |
| `skill` | SkillResolver | Skill resolution |

### Advanced Nodes

| LangGraph | LangFlow | Description |
|----------|---------|-------------|
| `chat` | Chat | Chat interface |
| `agent` | Agent | Agent execution |
| `chain` | LLMChain | LLM chain |
| `rag` | VectorStore | RAG/vector store |

## Tool Handling

Tools are preserved with:
- Tool name
- Tool ID
- Input/output schemas
- Retry/timeout metadata

Multi-tool nodes are mapped to ToolChainComponent.

## Skill Handling

Skills are preserved with:
- Skill ID
- Slug
- Skill type
- Scope (workflow/node)

## Memory Support

Memory bindings are preserved with:
- Memory type
- Scope
- Injection point

## Approval/Governance

Approval nodes are preserved with:
- Policy ID
- Risk level
- Approver type

## API Usage

### Compile a workflow

```bash
POST /api/v1/frameworks/langgraph/compile-to-langflow

{
  "name": "My Workflow",
  "description": "A test workflow",
  "nodes": [
    {"id": "start", "type": "start", "data": {}},
    {"id": "llm_node", "type": "llm", "data": {"model": "gpt-4"}},
    {"id": "end", "type": "end", "data": {}}
  ],
  "edges": [
    {"source": "start", "target": "llm_node"},
    {"source": "llm_node", "target": "end"}
  ]
}
```

### Import a workflow

```bash
POST /api/v1/frameworks/langgraph/import

{
  "graph_definition": {...},
  "import_to_storage": true
}
```

## Example: Full Workflow

Input LangGraph with tool + skill + approval + memory:

```json
{
  "name": "Full Workflow",
  "description": "Complete workflow with all bindings",
  "nodes": [
    {"id": "start", "type": "start", "data": {}},
    {"id": "search", "type": "tool", "data": {"tool_name": "web_search"}},
    {"id": "llm", "type": "llm", "data": {"model": "gpt-4"}},
    {"id": "skill_resolver", "type": "skill", "data": {"skill_id": "skill-1", "skill_slug": "analyze"}},
    {"id": "approval", "type": "approval", "data": {"policy_id": "policy-1", "risk_level": "medium"}},
    {"id": "memory", "type": "memory", "data": {"memory_type": "context", "scope": "workflow"}},
    {"id": "end", "type": "end", "data": {}}
  ],
  "edges": [
    {"source": "start", "target": "search"},
    {"source": "search", "target": "llm"},
    {"source": "llm", "target": "skill_resolver"},
    {"source": "skill_resolver", "target": "approval"},
    {"source": "approval", "target": "memory"},
    {"source": "memory", "target": "end"}
  ]
}
```

Returns:
```json
{
  "success": true,
  "langflow_flow": {...},
  "nodes_mapped": 7,
  "edges_mapped": 6,
  "tool_bindings_detected": ["web_search"],
  "skill_bindings_detected": ["analyze"],
  "approval_nodes_detected": ["policy-1"],
  "memory_bindings_detected": ["context:workflow"],
  "warnings": []
}
```

## Unsupported Constructs

When a node type is not directly supported:
1. Warning is emitted
2. Node is mapped to a generic `Passthrough` component
3. Original metadata is preserved

## Testing

Run tests:

```bash
pytest tests/framework/test_compiler.py -v
```