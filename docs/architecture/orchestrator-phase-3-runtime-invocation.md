# Orchestrator Phase 3: Runtime Invocation

This document describes Phase 3 runtime invocation implementation.

---

## Overview

Phase 3 adds real runtime invocation with adapters. The orchestrator now calls actual runtime adapters instead of stubbed execution.

---

## Components

| File | Description |
|------|-------------|
| `app/orchestrator/runtime_invoker.py` | Runtime invocation orchestration |
| `app/orchestrator/runtime_adapters.py` | Runtime-specific adapters |

---

## Runtime Invoker

### Responsibilities

1. **Adapter Selection** - Maps runtime ID to adapter
2. **Invocation** - Calls adapter with normalized input
3. **Error Handling** - Handles failures, triggers fallback
4. **Output Normalization** - Returns consistent RuntimeOutput

### Usage

```python
from app.orchestrator.runtime_invoker import get_runtime_invoker, RuntimeOutput

invoker = get_runtime_invoker()

output = invoker.invoke(
    runtime_id="openai_agents",
    state=execution_state,
    request=orchestrator_request,
)

# Normalized output
print(output.status)  # success/failed
print(output.output_text)
print(output.usage)  # {input_tokens, output_tokens}
print(output.tool_calls)
print(output.warnings)
print(output.raw_ref)
```

---

## Runtime Adapters

### Adapter Types

| Adapter | Runtime | Status |
|---------|---------|--------|
| `OpenAIAgentsAdapter` | OpenAI Agents SDK | PARTIALLY STUBBED |
| `ClaudeWorkerAdapter` | Claude Agent SDK | PARTIALLY STUBBED |
| `GenericWorkerAdapter` | Generic fallback | STUBBED |

### Base Interface

```python
class BaseRuntimeAdapter:
    def execute(
        self,
        state: ExecutionState,
        request: OrchestratorRequest,
    ) -> RuntimeOutput:
        """Execute via runtime"""
        
    def execute_fallback(
        self,
        request: OrchestratorRequest,
    ) -> RuntimeOutput:
        """Execute fallback when primary fails"""
```

### Normalized Output

```python
class RuntimeOutput:
    status: str          # success, failed, timeout
    output_text: str     # Main text output
    structured_output: Optional[Dict]  # JSON/structured data
    usage: Dict          # {input_tokens, output_tokens}
    tool_calls: List     # Tool invocations
    warnings: List       # Warnings (e.g., "using stub")
    raw_ref: Dict        # Debug/reference info
    error: Optional[str] # Error message if failed
```

---

## Adapter Details

### OpenAIAgentsAdapter

```python
# Checks for OPENAI_API_KEY
# TODO: Real SDK invocation when configured
# Currently returns stub with usage tracking
```

**Current Behavior**:
- Checks `OPENAI_API_KEY` environment variable
- If not set, returns stub response with warning
- Tracks estimated token usage

### ClaudeWorkerAdapter

```python
# Checks for ANTHROPIC_API_KEY
# TODO: Real API invocation when configured
# Currently returns stub with usage tracking
```

**Current Behavior**:
- Checks `ANTHROPIC_API_KEY` environment variable
- If not set, returns stub response with warning
- Tracks estimated token usage

### GenericWorkerAdapter

```python
# Generic fallback for any runtime
# Always returns stub response
```

---

## Execution Flow

```
ORCHESTRATOR EXECUTION STAGE
         │
         ▼
┌─────────────────────┐
│  Runtime Invoker   │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│  Get Adapter       │
│  (by runtime_id)    │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│  Adapter.execute()  │
└─────────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
Success    Error
    │         │
    ▼         ▼
┌───────┐ ┌──────────┐
│Output │ │ Fallback │
└───────┘ └──────────┘
```

---

## Error Handling

### RuntimeInvocationError

```python
class RuntimeInvocationError(Exception):
    runtime_id: str
    is_retryable: bool
```

### Fallback Behavior

If primary runtime fails:
1. Check if error is retryable
2. If retryable, try `generic` adapter
3. If fallback fails, return failed output

---

## Extension Hooks

### Custom Adapter

```python
invoker = get_runtime_invoker()

class MyCustomAdapter(BaseRuntimeAdapter):
    def execute(self, state, request):
        # Custom logic
        return RuntimeOutput(status="success", output_text="...")

invoker.register_adapter("my_runtime", MyCustomAdapter())
```

### Future: Real OpenAI Integration

```python
class OpenAIAgentsAdapter(BaseRuntimeAdapter):
    def _ensure_initialized(self):
        if not self._initialized:
            from openai import OpenAI
            self._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self._initialized = True
    
    def execute(self, state, request):
        self._ensure_initialized()
        
        response = self._client.agents.run(
            agent_id=request.agent_id,
            input=request.request_text,
        )
        
        return RuntimeOutput(
            status="success",
            output_text=response.output,
            usage=response.usage,
        )
```

---

## Test Coverage

Tests in `tests/test_orchestrator_phase3.py`:

| Test | Description |
|------|-------------|
| `test_runtime_output_creation` | Create RuntimeOutput |
| `test_runtime_output_to_dict` | Convert to dict |
| `test_generic_adapter_execute` | Generic adapter execution |
| `test_generic_adapter_fallback` | Generic fallback |
| `test_openai_adapter_stub` | OpenAI stub response |
| `test_claude_adapter_stub` | Claude stub response |
| `test_get_adapter` | Get adapter by ID |
| `test_invoker_creation` | Create invoker |
| `test_invoker_generic_runtime` | Invoke generic |
| `test_invoker_unknown_runtime` | Unknown falls back |
| `test_invoker_returns_normalized_output` | Normalized shape |
| `test_invoker_captures_usage` | Usage tracking |
| `test_invoker_adds_raw_ref` | Debug reference |
| `test_custom_adapter_registration` | Custom adapter |
| `test_output_has_all_fields` | All output fields |
| `test_output_defaults` | Default values |

---

## What Is Real vs Placeholder After Phase 3

| Component | Status |
|-----------|--------|
| Task detection | ✅ REAL |
| Runtime selection | ✅ REAL |
| Channel/Branch/Worker context | ✅ REAL |
| Context budget check | ✅ REAL |
| Tool resolution | ✅ REAL |
| Skill resolution | ✅ REAL |
| Policy gate | ✅ REAL |
| Guardrails | ✅ REAL |
| Approval workflow | ✅ REAL |
| **Runtime invocation path** | ✅ REAL |
| **Adapter selection** | ✅ REAL |
| **Normalized output** | ✅ REAL |
| **Error handling** | ✅ REAL |
| **Usage tracking** | ✅ REAL |
| Real OpenAI SDK | 🔶 PLACEHOLDER |
| Real Claude API | 🔶 PLACEHOLDER |
| Full access control | 🔶 PLACEHOLDER |
| OPA integration | 🔶 PLACEHOLDER |
| Real compaction | 🔶 PLACEHOLDER |

---

## Next Steps

1. **Real OpenAI Integration** - Connect actual OpenAI Agents SDK
2. **Real Claude Integration** - Connect actual Claude API
3. **Access Control** - Integrate fine-grained access control
4. **Compaction Execution** - Real context compaction
5. **Audit Integration** - Full audit logging

---

_End of Orchestrator Phase 3 Documentation_