# LangGraph → LangFlow Compiler

This compiler translates LangGraph-style workflow definitions into LangFlow-compatible flow structures that can be imported, visualized, edited, and exported back into Decide.

## Round-Trip Flow

The compiler enables this complete round-trip:

```
LangGraph Definition → LangFlow JSON → Decide Storage → (roundtrip) → LangGraph
```

## Overview

The compiler is a translation layer that preserves metadata, tools, skills, memory bindings, and approval/governance constructs when converting between frameworks.

## Real Import Integration

The `/frameworks/langgraph/import` endpoint does a real round-trip:

1. **Compile**: LangGraph → LangFlow JSON
2. **Store**: Creates WorkflowDefinition in Decide database
3. **Version**: Creates WorkflowVersion record
4. **Nodes**: Imports nodes with rich metadata preservation
5. **Edges**: Imports edges with node mappings

Returns real workflow_id that can be validated, published, and run.

## API Usage

### Compile Only

```bash
POST /api/v1/frameworks/langgraph/compile-to-langflow

{
  "name": "My Workflow",
  "nodes": [...],
  "edges": [...]
}
```

Returns LangFlow JSON with diagnostics.

### Compile + Import

```bash
POST /api/v1/frameworks/langgraph/import?tenant_id=tenant-123

{
  "name": "My Workflow",
  "nodes": [...],
  "edges": [...]
}
```

Returns real workflow_id in Decide:

```json
{
  "success": true,
  "workflow_id": "uuid-here",
  "version_id": "version-uuid",
  "nodes_imported": 5,
  "edges_imported": 4
}
```

### Validate

```bash
GET /api/v1/frameworks/langgraph/validate?graph_definition={...}
```

### Roundtrip Export

```bash
GET /api/v1/frameworks/roundtrip/{workflow_id}
```

Exports a stored workflow back to LangGraph format.
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
| `condition` | DecisionGate | Conditional routing |
| `approval` | ApprovalGate | Approval checkpoint |
| `memory` | MemoryRecall | Memory fetch |
| `skill` | SkillResolver | Skill resolution |

## Metadata Preservation

The compiler preserves:
- **Tools**: tool_name, tool_id, input/output schemas
- **Skills**: skill_id, slug, type, scope (workflow/node)
- **Memory**: memory_type, scope, injection_point
- **Approval**: policy_id, risk_level, approver_type

## Testing

```bash
pytest tests/framework/test_compiler.py -v
```

Run 9 tests covering compile, import, diagnostics, and full round-trips.
