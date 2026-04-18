# Runtime Selection Implementation

This document describes how runtime selection integrates with the existing backend selection flow in Runtime Architecture v2.

---

## 1. Purpose

The purpose of this document is to:

1. **Map runtime to backend** - Show how runtime selection translates to backend selection
2. **Integrate with control plane** - Connect runtime selection to existing policy resolution
3. **Enable fallback** - Show how runtime fallback works alongside backend fallback
4. **Preserve audit** - Ensure runtime selection is captured in execution trace

---

## 2. Integration Points

### Current Backend Flow (Existing)

```
execution_request created
    → policy_resolution (evaluate tenant policy)
    → backend_selection (select preferred backend)
    → execution (call backend API)
    → usage_record (capture cost)
    → execution_history (audit)
```

### Runtime Selection Flow (New)

```
execution_request created
    → runtime_selection (select runtime based on task_type)
    → [runtime maps to backend via registry]
    → backend_selection (existing flow unchanged)
    → execution
```

### Key Insight

**Runtime selection happens BEFORE backend selection.** The runtime determines:
- Which runtime engine to use (OpenAI Agents SDK, Claude, etc.)
- Which backend that runtime should call
- Default model configuration

---

## 3. Runtime Registration

### Registry Schema

```python
# app/core/runtime_registry.py
class WorkerRuntime(BaseModel):
    runtime_id: str           # e.g., "claude_agent"
    runtime_type: RuntimeType  # LANGGRAPH, OPENAI_AGENTS, etc.
    backend_provider: str      # e.g., "anthropic"
    backend_model: str        # e.g., "claude-sonnet-4"
    endpoint_url: str        # Optional override
```

### Default Runtimes

| Runtime ID | Type | Provider | Model | Best For |
|-----------|------|----------|-------|----------|
| openai_agents | OPENAI_AGENTS_SDK | openai | gpt-4o | General conversation |
| claude_agent | CLAUDE_AGENT_SDK | anthropic | claude-sonnet-4 | Premium coding |
| deep_agents | DEEP_AGENTS | openai | gpt-4-turbo | Long-running autonomous |
| crewai | CREWAI | openai | gpt-4o | Team collaboration |
| langchain | LANGCHAIN | openai | gpt-4o-mini | Lightweight tasks |

---

## 4. Runtime Selection Logic

### Step 1: Detect Task Type

```python
# Detect from execution_request.goal and execution_request.capability
task_type = detect_task_type(
    goal="Refactor the authentication module",
    capability="coding"
)
# Returns: "coding"
```

### Step 2: Select Runtime

```python
# Based on task_type and tenant policy
runtime = select_runtime(
    task_type="coding",
    tenant_id="tenant-123"
)
# Returns: WorkerRuntime(runtime_id="claude_agent", ...)
```

### Step 3: Map to Backend

```python
# Runtime already knows which backend to use
backend_id = runtime.backend_provider  # "anthropic"
backend_model = runtime.backend_model    # "claude-sonnet-4"
```

---

## 5. Integration with Backend Selection

### Existing BackendSelection Table (Unchanged)

```sql
-- Still used for audit and fallback
CREATE TABLE backend_selection (
    id VARCHAR(36) PRIMARY KEY,
    execution_request_id VARCHAR(36) REFERENCES execution_request(id),
    selected_backend VARCHAR(50) NOT NULL,
    selection_order INTEGER DEFAULT 1,
    selected_at TIMESTAMP DEFAULT NOW()
);
```

### New Runtime Link

We extend the BackendSelection to include runtime context:

```python
@dataclass
class BackendSelection:
    id: str
    execution_request_id: str
    selected_backend: str           # Backend provider (existing)
    selected_runtime: str        # NEW: Runtime ID
    runtime_type: str          # NEW: Runtime type
    selection_order: int = 1
    selected_at: datetime = None
```

### Updated Selection Flow

```python
async def select_backend_for_request(
    execution_request: ExecutionRequest,
    tenant_id: str
) -> BackendSelection:
    # Step 1: Runtime selection (NEW)
    task_type = detect_task_type(
        execution_request.goal,
        execution_request.capability
    )
    runtime = await select_runtime(task_type, tenant_id)
    
    # Step 2: Map to backend (existing)
    backend_id = runtime.backend_provider
    backend_model = runtime.backend_model
    
    # Step 3: Create selection records
    backend_selection = BackendSelection(
        id=str(uuid4()),
        execution_request_id=execution_request.id,
        selected_backend=backend_id,
        selected_runtime=runtime.runtime_id,
        runtime_type=runtime.runtime_type.value
    )
    
    return backend_selection
```

---

## 6. Task Type Detection Examples

### Example 1: Coding

```
Goal: "Refactor the authentication module for better error handling"
Capability: "coding"

Detection: 
  - capability contains "coding" → return "coding"
  - Fallback: goal contains "refactor", "implement", "fix" → return "coding"

Runtime Selected: "claude_agent"
Backend: "anthropic" / "claude-sonnet-4"
```

### Example 2: General Conversation

```
Goal: "What tasks do I have due this week?"
Capability: None

Detection:
  - capability missing → use goal heuristics
  - goal contains "what", "list", "how" → return "conversation"

Runtime Selected: "openai_agents"
Backend: "openai" / "gpt-4o"
```

### Example 3: Long-Running

```
Goal: "Research the entire literature on topic X and create a comprehensive summary"
Capability: None

Detection:
  - goal contains "entire", "comprehensive", "full" → return "autonomous"

Runtime Selected: "deep_agents"
Backend: "openai" / "gpt-4-turbo"
```

### Example 4: Collaboration

```
Goal: "Work with the research team to analyze this dataset"
Capability: None

Detection:
  - goal contains "collaborate", "team", "work together" → return "collaboration"

Runtime Selected: "crewai"
Backend: "openai" / "gpt-4o"
```

### Example 5: Simple Task

```
Goal: "What is my current quota?"
Capability: None

Detection:
  - goal is simple question → return "simple"

Runtime Selected: "langchain"
Backend: "openai" / "gpt-4o-mini"
```

---

## 7. Policy Integration

### Tenant Runtime Policy

```python
class RuntimeSelectionPolicy(BaseModel):
    policy_id: str
    tenant_id: str
    rules: list[RuntimeSelectionRule]  # Task-type specific rules
    default_for_unknown: RuntimeType
    enabled: bool = True
```

### Example Tenant Policies

| Tenant | Coding Policy | Conversation Policy |
|--------|--------------|---------------------|
| acme_corp | claude_agent | openai_agents |
| startup_inc | openai_agents | openai_agents |
| research_org | deep_agents | openai_agents |

### Policy Override

Tenants can override runtime selection via tenant_policy table:

```sql
-- Existing table can be extended
ALTER TABLE tenant_policy 
ADD COLUMN runtime_selection_policy JSONB;
```

---

## 8. Fallback Chain

### Runtime Fallback

```
Requested Runtime Unavailable
    → Try fallback runtime defined in policy
    → Try default runtime
    → Return error
```

### Backend Fallback (Existing)

```
Selected Backend Fails
    → FallbackEvent recorded
    → Try next backend in chain
    → Continue until success or exhaust
```

### Combined Flow

```python
async def execute_with_runtime_and_backend_fallback(
    execution_request: ExecutionRequest
) -> ExecutionResult:
    # 1. Select runtime
    runtime = await select_runtime(
        execution_request.goal,
        execution_request.tenant_id
    )
    
    # 2. Try primary backend with runtime
    result = await execute_with_runtime(runtime, execution_request)
    
    if result.success:
        return result
    
    # 3. Backend fallback (existing flow)
    for fallback_backend in get_backend_fallback_chain(runtime):
        result = await execute_with_backend(
            fallback_backend, 
            execution_request
        )
        if result.success:
            # Record fallback event
            await record_fallback_event(
                execution_request.id,
                runtime.backend_provider,
                fallback_backend
            )
            return result
    
    # 4. Runtime fallback (new)
    if runtime.fallback_runtime:
        fallback_runtime = get_runtime(runtime.fallback_runtime)
        result = await execute_with_runtime(
            fallback_runtime,
            execution_request
        )
        return result
    
    # 5. All failed
    raise ExecutionError("All runtimes and backends failed")
```

---

## 9. Audit Trail

### Execution History Recording

```python
async def record_runtime_selection(
    execution_request_id: str,
    runtime: WorkerRuntime
):
    # Record in execution_history
    await db.execute("""
        INSERT INTO execution_history 
        (id, execution_request_id, event_type, event_data)
        VALUES (%s, %s, 'runtime_selected', %s)
    """, [
        str(uuid4()),
        execution_request_id,
        json.dumps({
            "runtime_id": runtime.runtime_id,
            "runtime_type": runtime.runtime_type.value,
            "backend_provider": runtime.backend_provider,
            "backend_model": runtime.backend_model
        })
    ])
```

### Event Data

```json
{
  "event_type": "runtime_selected",
  "event_data": {
    "runtime_id": "claude_agent",
    "runtime_type": "claude_agent_sdk",
    "backend_provider": "anthropic",
    "backend_model": "claude-sonnet-4"
  },
  "task_type": "coding",
  "selected_at": "2025-04-14T10:00:00Z"
}
```

---

## 10. Usage Recording

### Cost Tracking (Existing)

Runtime selection is captured in usage_record:

```python
@dataclass
class UsageRecord:
    id: str
    execution_request_id: str
    backend_used: str           # From runtime.backend_provider
    provider: str          # From runtime.backend_provider  
    model: str             # From runtime.backend_model
    runtime_used: str     # NEW: From runtime.runtime_id
    input_tokens: int
    output_tokens: int
```

---

## 11. API Endpoints

### GET /api/v1/runtimes

List available runtimes:

```python
@router.get("/runtimes")
async def list_runtimes(
    registry: WorkerRuntimeRegistry = Depends(get_registry)
):
    return {
        "runtimes": [
            {
                "runtime_id": r.runtime_id,
                "runtime_type": r.runtime_type.value,
                "backend_provider": r.backend_provider,
                "backend_model": r.backend_model,
                "capabilities": r.capabilities.model_dump(),
                "enabled": r.enabled
            }
            for r in registry.list_runtimes()
        ]
    }
```

### GET /api/v1/runtimes/{runtime_id}

Get runtime details:

```python
@router.get("/runtimes/{runtime_id}")
async def get_runtime(
    runtime_id: str,
    registry: WorkerRuntimeRegistry = Depends(get_registry)
):
    runtime = registry.get_runtime(runtime_id)
    if not runtime:
        raise HTTPException(404, "Runtime not found")
    return runtime
```

### POST /api/v1/runtimes/select

Select runtime for a request:

```python
@router.post("/runtimes/select")
async def select_runtime_for_request(
    goal: str,
    capability: str | None = None,
    tenant_id: str,
    registry: WorkerRuntimeRegistry = Depends(get_registry)
):
    task_type = detect_task_type(goal, capability)
    runtime = registry.select_runtime(task_type, tenant_id)
    return {
        "task_type": task_type,
        "runtime": {
            "runtime_id": runtime.runtime_id,
            "runtime_type": runtime.runtime_type.value,
            "backend_provider": runtime.backend_provider,
            "backend_model": runtime.backend_model
        }
    }
```

---

## 12. Summary: How This Maps to Current Backend Flow

### Current Flow (Unchanged)

```
1. execution_request created
     ↓
2. policy_resolution evaluates tenant policy
     ↓
3. backend_selection selects preferred backend
     ↓
4. execute() calls backend API
     ↓
5. usage_record captures cost
     ↓
6. execution_history records audit
```

### New Flow (With Runtime)

```
1. execution_request created
     ↓
2. runtime_selection selects runtime (NEW)
     ↓ (runtime knows backend)
3. policy_resolution evaluates tenant policy
     ↓
4. backend_selection selects preferred backend (unchanged)
     ↓
5. execute() calls backend API (unchanged)
     ↓
6. usage_record captures cost + runtime (extended)
     ↓
7. execution_history records audit + runtime (extended)
```

### Key Points

1. **Runtime selection is NEW** - Happens before backend selection
2. **Backend flow is UNCHANGED** - Existing backend_selection, execution, usage still work
3. **Runtime provides context** - runtime_id available in usage_record for cost allocation
4. **Full audit** - Runtime selection recorded in execution_history

---

## Appendix A: Runtime Capability Matrix

| Capability | openai_agents | claude_agent | deep_agents | crewai | langchain |
|------------|---------------|--------------|-------------|--------|----------|
| Multi-turn chat | ✅ | ❌ | ❌ | ✅ | ❌ |
| Tool use | ✅ | ✅ | ✅ | ✅ | ✅ |
| Coding | ⚠️ | ✅ | ⚠️ | ⚠️ | ❌ |
| Long-running | ❌ | ❌ | ✅ | ⚠️ | ❌ |
| Checkpoint | ❌ | ✅ | ✅ | ⚠️ | ❌ |
| Parallel exec | ❌ | ❌ | ✅ | ✅ | ❌ |
| MCP support | ✅ | ❌ | ❌ | ❌ | ⚠️ |

---

## Appendix B: Example Policies

### Coding Priority

```python
RuntimeSelectionPolicy(
    policy_id="coding_priority",
    tenant_id="tenant_acme",
    rules=[
        RuntimeSelectionRule(
            task_type="coding",
            preferred_runtime=RuntimeType.CLAUDE_AGENT_SDK,
            fallback_runtime=RuntimeType.LANGCHAIN,
            reason="Premium coding requires strong reasoning"
        )
    ],
    default_for_unknown=RuntimeType.OPENAI_AGENTS_SDK
)
```

### General Purpose

```python
RuntimeSelectionPolicy(
    policy_id="general",
    tenant_id="tenant_startup",
    rules=[],
    default_for_unknown=RuntimeType.OPENAI_AGENTS_SDK
)
```

### Autonomous Heavy

```python
RuntimeSelectionPolicy(
    policy_id="autonomous_heavy",
    tenant_id="tenant_research",
    rules=[
        RuntimeSelectionRule(
            task_type="autonomous",
            preferred_runtime=RuntimeType.DEEP_AGENTS,
            fallback_runtime=RuntimeType.CREWAI,
            reason="Long-running research with checkpoints"
        ),
        RuntimeSelectionRule(
            task_type="research",
            preferred_runtime=RuntimeType.DEEP_AGENTS,
            fallback_runtime=RuntimeType.CLAUDE_AGENT_SDK,
            reason="Research benefits from deep context"
        )
    ],
    default_for_unknown=RuntimeType.OPENAI_AGENTS_SDK
)
```

---

_End of Runtime Selection Implementation_