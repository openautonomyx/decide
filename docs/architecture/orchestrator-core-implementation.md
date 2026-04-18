# Orchestrator Core Implementation

This document describes the Phase 1 orchestrator core implementation.

---

## Overview

The orchestrator engine coordinates request execution through the Phase 0 services. It implements a 10-stage execution pipeline from intake to result aggregation.

### Components

| File | Description |
|------|-------------|
| `app/orchestrator/types.py` | Type definitions |
| `app/orchestrator/state.py` | Execution state management |
| `app/orchestrator/router.py` | Task detection and runtime selection |
| `app/orchestrator/engine.py` | Core execution engine |

---

## Execution Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR PIPELINE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. INTAKE          ───►  Create execution ID                           │
│                                                                          │
│  2. STATE_INIT      ───►  Initialize ExecutionState                    │
│                                                                          │
│  3. TASK_DETECTION  ───►  Detect task type (keyword matching)          │
│       │                                                                   │
│       │                    TaskType:                                    │
│       │                    - coding                                      │
│       │                    - conversation                                │
│       │                    - autonomous                                  │
│       │                    - collaboration                                │
│       │                    - research                                    │
│       │                    - simple                                      │
│       ▼                                                                   │
│  4. RUNTIME_SELECTION ──► Select runtime via RuntimeRegistryService    │
│       │                                                                   │
│       │                    Uses task_type + tenant policy               │
│       ▼                                                                   │
│  5. CONTEXT_SETUP   ───►  Create channel/branch/worker                 │
│       │                   via ChannelService                             │
│       ▼                                                                   │
│  6. BUDGET_CHECK    ───►  Check context budget                         │
│       │                   via ContextBudgetService                      │
│       │                                                                   │
│       │                   Returns: should_compact                       │
│       ▼                                                                   │
│  7. TOOL_RESOLUTION ───►  Resolve required tools                      │
│  8. SKILL_RESOLUTION ──►  Resolve required skills                      │
│       │                                                                   │
│       ▼                                                                   │
│  9. EXECUTION       ───►  STUBBED - would call runtime                 │
│       │                                                                   │
│       │                   Currently: returns processed text            │
│       │                   Future: calls runtime.execute()               │
│       ▼                                                                   │
│ 10. COMPACTION_CHECK ───► Determine if compaction needed              │
│                                                                          │
│ 11. RESULT          ───►  Build OrchestratorResult                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## What Is Real vs Stubbed

### Real (Implemented)

| Component | Status | Notes |
|-----------|--------|-------|
| ExecutionState management | ✅ REAL | In-memory store |
| Task type detection | ✅ REAL | Keyword-based matching |
| Runtime selection | ✅ REAL | Delegates to RuntimeRegistryService |
| Channel/Branch creation | ✅ REAL | Creates via ChannelService |
| Worker creation | ✅ REAL | Creates via WorkerService |
| Context budget check | ✅ REAL | Checks budget via ContextBudgetService |
| Tool/Skill resolution | ✅ REAL | Resolves via ToolRegistryService/SkillService |
| State tracking | ✅ REAL | Tracks stages, tokens, status |
| Result aggregation | ✅ REAL | Builds normalized OrchestratorResult |

### Stubbed / Placeholder

| Component | Status | Notes |
|-----------|--------|-------|
| Actual execution | 🔶 STUBBED | Returns processed text only |
| Runtime invocation | 🔶 STUBBED | Would call runtime.execute() |
| Policy evaluation | 🔶 PLACEHOLDER | Hook exists, not integrated |
| Guardrails | 🔶 PLACEHOLDER | Hook exists, not integrated |
| HITL approval | 🔶 PLACEHOLDER | NextAction includes needs_approval |
| Compaction execution | 🔶 PLACEHOLDER | Triggers flag, not executed |
| Audit logging | 🔶 PLACEHOLDER | Audit refs present but empty |
| Persistence | 🔶 PLACEHOLDER | In-memory only |

---

## API Integration

The orchestrator reuses these Phase 0 services:

```python
from app.services.runtime import get_runtime_registry_service
from app.services.channel import get_channel_service, get_branch_service, get_worker_service
from app.services.tool import get_tool_registry_service
from app.services.skill import get_skill_service
from app.services.context import get_context_budget_service, get_token_accounting_service
```

---

## Extension Hooks

The orchestrator includes explicit hooks for:

### Policy Governance

```python
# In router.py - can integrate PolicyService
def select_runtime(self, task_type, tenant_id, preferred_runtime=None):
    # TODO: Check PolicyService for runtime_selection_policy
    # TODO: Apply tenant-specific runtime policies
```

### Guardrails

```python
# In engine.py - before execution stage
def _stage_execution(self, state, request):
    # TODO: Check GuardrailService before execution
    # TODO: Validate input/output against guardrails
```

### HITL Approval

```python
# In result aggregation
if needs_human_approval:
    return OrchestratorResult(
        next_action=NextAction.NEEDS_APPROVAL,
        status=OrchestratorStatus.AWAITING_APPROVAL,
    )
```

### Compaction Execution

```python
# In compaction check stage
if should_compact:
    # TODO: Call CompactionService to generate summary
    # TODO: Truncate context and continue execution
```

---

## Usage

### Basic Execution

```python
from app.orchestrator import execute_request, OrchestratorRequest

request = OrchestratorRequest(
    tenant_id="tenant-123",
    user_id="user-456",
    request_text="write a python function to calculate fibonacci",
)

result = execute_request(request)

print(f"Status: {result.status}")
print(f"Runtime: {result.selected_runtime}")
print(f"Tools: {result.selected_tools}")
print(f"Output: {result.output_summary}")
```

### With Options

```python
request = OrchestratorRequest(
    tenant_id="tenant-123",
    user_id="user-456",
    request_text="search the web for quantum computing",
    preferred_runtime="langgraph",
    required_tools=["search_web"],
    required_skills=["web_search"],
)

result = execute_request(request)
```

### Response Structure

```python
{
    "execution_request_id": "exec-abc123",
    "status": "completed",
    "selected_runtime": "langgraph",
    "selected_tools": ["search_web"],
    "selected_skills": [],
    "branch_id": "branch-xyz",
    "output_summary": "Processed: search the web...",
    "next_action": "complete",
    "audit_refs": {
        "execution_id": "exec-abc123",
        "thread_id": "thread-123",
        "branch_id": "branch-xyz",
        "worker_id": "worker-789"
    },
    "metadata": {
        "task_type": "research",
        "input_tokens": 150,
        "output_tokens": 50,
        "compaction_triggered": false
    },
    "stages_completed": [
        "intake",
        "state_init",
        "task_detection",
        "runtime_selection",
        "context_setup",
        "budget_check",
        "tool_resolution",
        "skill_resolution",
        "execution",
        "compaction_check",
        "result_aggregation",
        "complete"
    ]
}
```

---

## Test Coverage

Tests are in `tests/test_orchestrator.py`:

```bash
pytest tests/test_orchestrator.py -v
```

### Test Cases

- `test_execute_simple_request` - Basic execution
- `test_execute_coding_request` - Coding task detection
- `test_execute_with_thread` - Thread context
- `test_execute_with_preferred_runtime` - Runtime override
- `test_execute_with_required_tools` - Tool resolution
- `test_execute_with_required_skills` - Skill resolution
- `test_execute_research_request` - Research task
- `test_execute_autonomous_request` - Autonomous task
- `test_result_has_audit_refs` - Audit references
- `test_result_has_stages_completed` - Stage tracking

---

## Next Steps (Phase 2)

1. **Policy Integration** - Integrate PolicyService for runtime selection
2. **Guardrails Integration** - Add input/output validation
3. **HITL Approval** - Implement approval flow
4. **Compaction Execution** - Run actual compaction
5. **Runtime Invocation** - Connect to real runtimes
6. **Persistence** - Add Redis/DB for state
7. **Audit Logging** - Full audit trail

---

_End of Orchestrator Core Implementation_