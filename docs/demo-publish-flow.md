# Demo: Publish Flow End-to-End

This document describes the end-to-end flow for running a publish workflow through Decide.

## Overview

The demo scenario: Langflow-authored workflow → Decide import/compile → workflow run → inspect run detail with memory + skills attached.

## Prerequisites

- Decide API running (at `/api/v1` prefix via `app/main.py`)
- Database migrated (Alembic head)
- At least one tenant exists

## Step 1: Create a Workflow (Import from Langflow)

Import a simple publish workflow with nodes: start → llm → condition → tool → end.

```bash
curl -X POST "http://localhost:8000/api/v1/workflows/import/langflow" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "d9164904-e2a3-4371-a70c-9f52834c1e5a",
    "name": "Publish Flow Demo",
    "langflow_data": {
      "nodes": [
        {"id": "start_1", "type": "ChatInput", "data": {"label": "Start"}},
        {"id": "llm_1", "type": "Prompt", "data": {"label": "Generate Content", "model": "gpt-4"}},
        {"id": "cond_1", "type": "Router", "data": {"label": "Check Quality"}},
        {"id": "tool_1", "type": "Tool", "data": {"label": "Publish", "tool_name": "publish"}},
        {"id": "end_1", "type": "ChatOutput", "data": {"label": "Done"}}
      ],
      "edges": [
        {"source": "start_1", "target": "llm_1"},
        {"source": "llm_1", "target": "cond_1"},
        {"source": "cond_1", "target": "tool_1", "sourceHandle": "true"},
        {"source": "tool_1", "target": "end_1"}
      ]
    }
  }'
```

Response:
```json
{
  "workflow_id": "wf-xxx",
  "status": "imported",
  "message": "Workflow imported successfully"
}
```

## Step 2: Validate

```bash
curl -X POST "http://localhost:8000/api/v1/workflows/{workflow_id}/validate"
```

Response:
```json
{
  "valid": true,
  "errors": []
}
```

## Step 3: Publish

```bash
curl -X POST "http://localhost:8000/api/v1/workflows/{workflow_id}/publish"
```

Response:
```json
{
  "workflow_id": "wf-xxx",
  "version_id": "v-xxx",
  "status": "published",
  "published_at": "2024-01-01T00:00:00Z"
}
```

## Step 4: Run the Workflow

```bash
curl -X POST "http://localhost:8000/api/v1/workflows/{workflow_id}/run"
```

Response:
```json
{
  "run_id": "run-xxx",
  "workflow_id": "wf-xxx",
  "status": "running"
}
```

## Step 5: Inspect Run Detail (with Memory + Skills)

```bash
curl "http://localhost:8000/api/v1/workflows/{workflow_id}/runs/{run_id}"
```

Response includes:
```json
{
  "id": "run-xxx",
  "workflow_id": "wf-xxx",
  "status": "completed",
  "final_output": "Workflow completed",
  "steps": [...],
  "memory_context": [
    {"id": "mem-xxx", "memory_type": "knowledge", "content": "..."}
  ],
  "resolved_skills": [
    {"id": "skill-xxx", "name": "Code Review", "skill_type": "prompt_skill"}
  ]
}
```

## Runtime Context

The run detail now exposes:
- `memory_context`: Active memory entries from the organization's memory space
- `resolved_skills`: Active skills scoped to the organization

These are resolved at runtime from the workflow's tenant_id.

## Expected Response Shape

```
GET /api/v1/workflows/{workflow_id}/runs/{run_id}

{
  "id": "uuid",
  "workflow_id": "uuid",
  "version_id": "uuid", 
  "status": "pending|running|completed|failed",
  "final_output": "...",
  "started_at": "ISO8601",
  "completed_at": "ISO8601|null",
  "error_message": "...",
  "steps": [
    {
      "node_id": "start_1",
      "node_type": "start",
      "status": "completed",
      "output": "Started workflow",
      "branch_decision": null,
      "error": null,
      "started_at": "ISO8601",
      "completed_at": "ISO8601"
    }
  ],
  "memory_context": [
    {"id": "uuid", "memory_type": "knowledge", "content": "..."}
  ],
  "resolved_skills": [
    {"id": "uuid", "name": "...", "skill_type": "prompt_skill"}
  ]
}
```