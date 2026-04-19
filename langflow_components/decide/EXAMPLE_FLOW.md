# Example: Langflow → Decide Integration Flow

This document shows an example of how to use the Decide component pack
to create an end-to-end flow from Langflow to the Decide platform.

## Example Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User Input     │────▶│  SkillResolver  │────▶│ MemoryResolver  │
│   (request)      │     │  (tenant_id)      │     │  (tenant_id)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  (results)      │◀────│ ExportToDecide  │◀────│ PublishToLang   │
│  (LLM output)   │     │  (tenant_id)    │     │  (graph_def)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Configuration

Set the following environment variables:

```bash
# Point to your Decide API
export DECIDE_API_URL=http://localhost:8000

# Optional: API key for authentication
export DECIDE_API_KEY=your-api-key
```

## Component Setup

### 1. SkillResolver
- **tenant_id**: Your Decide tenant ID
- **skill_categories**: Optional comma-separated categories
- **routing_strategy**: auto, explicit, or llm_routed
- **Input**: A request text from user
- **Output**: Resolved skills

### 2. MemoryResolver
- **tenant_id**: Your Decide tenant ID
- **scope_type**: organization, product, workflow, or run
- **scope_id**: The ID of the scope to resolve memory for
- **max_history**: Max items to return (default: 10)
- **Input**: A scope_id
- **Output**: Memory context + checkpoint_id

### 3. ExportToDecide
- **tenant_id**: Your Decide tenant ID
- **thread_id**: Optional thread for continuation
- **export_format**: json or yaml
- **Input**: Workflow results
- **Output**: Execution reference with ID

### 4. PublishToLangGraph
- **graph_name**: Name for the published graph
- **checkpointer**: memory, sqlite, or postgres
- **Input**: Graph definition {nodes: [], edges: []}
- **Output**: Compiled LangGraph

## Running the Flow

1. Start Decide API: `uvicorn app.main:app --reload --port 8000`
2. Configure components with tenant_id
3. Run the flow in Langflow
4. Results are exported to Decide

## API Fallback Behavior

If the Decide API is unavailable, components will:
- Return stub responses with `status: "stub" and `fallback: true`
- Include error message in the response
- Flow continues without failure

This allows for:
- Offline development/testing
- Graceful degradation
- Easy debugging

## Testing Without Decide

Use stub behavior by leaving tenant_id empty:

```python
# In SkillResolver, leave tenant_id empty
skill_categories = "code-review,security"
# Result: Returns empty skills with stub status

# In MemoryResolver, leave tenant_id empty
scope_id = "test-workflow-123"
# Result: Returns empty context with stub status

# In ExportToDecide, leave tenant_id empty
# Result: Returns stub execution_id with error "tenant_id required"
```

## Real API Integration

Set tenant_id to enable real API calls:

```python
# In component config:
tenant_id = "tenant-abc123"
# Components will call:
# - POST /api/v1/execution/requests
# - POST /api/v1/memory/resolve
# - GET /api/v1/skills/resolve
```