# Runtime & Memory Implementation

This document describes the runtime and memory infrastructure wiring for Runtime Architecture v2.

---

## 1. Overview

This implementation adds:

1. **Runtime Support Modules** - Runtime selection, types, and configuration
2. **Memory Abstraction Layers** - Working, episodic, semantic, checkpoint, and cortex memory
3. **Configuration** - Environment variable support for new features

These are **additive** - they do not replace existing control-plane or workflow entities.

---

## 2. What Is Implemented

### 2.1 Runtime Modules

| Module | Status | Description |
|--------|--------|-------------|
| `app/core/runtime_types.py` | ✅ IMPLEMENTED | Type definitions (RuntimeType, TaskType, etc.) |
| `app/core/runtime_config.py` | ✅ IMPLEMENTED | Configuration from environment |
| `app/core/runtime_registry.py` | ✅ IMPLEMENTED | Registry with 5 default runtimes |
| `app/core/runtime_selection.py` | ✅ IMPLEMENTED | Selection service with detection |

### 2.2 Memory Modules

| Module | Status | Description |
|--------|--------|-------------|
| `app/memory/types.py` | ✅ IMPLEMENTED | Type definitions |
| `app/memory/working_memory.py` | ✅ IMPLEMENTED | Redis hot working memory |
| `app/memory/episodic_memory.py` | ✅ PARTIAL | Redis cache + Postgres |
| `app/memory/semantic_memory.py` | 🔶 ADAPTER | SingleStore adapter interface |
| `app/memory/checkpoints.py` | 🔶 ADAPTER | Postgres adapter interface |
| `app/memory/cortex.py` | ✅ PARTIAL | Redis cache + Postgres adapter |

### 2.3 Configuration

| Config | Status | Description |
|--------|--------|-------------|
| `.env.example` | ✅ UPDATED | Added runtime and memory env vars |
| `runtime_config.py` | ✅ IMPLEMENTED | Config loading from env |

---

## 3. What Is Adapter-Only

The following modules have interfaces defined but require external infrastructure:

| Module | External Dependency | Phase |
|--------|-------------------|-------|
| `semantic_memory.py` | SingleStore | Phase 2 |
| `checkpoints.py` | Postgres (existing) | Phase 2 |
| `cortex.py` | Redis (hot) + Postgres (archive) | Phase 2 |

These are **ready for integration** - once SingleStore is provisioned, the adapter can be connected.

---

## 4. Module Details

### 4.1 Runtime Types (`runtime_types.py`)

```python
# Core types
class RuntimeType(str, Enum):
    LANGGRAPH_ORCHESTRATOR = "langgraph"
    OPENAI_AGENTS_SDK = "openai_agents"
    CLAUDE_AGENT_SDK = "claude_agent"
    DEEP_AGENTS = "deep_agents"
    CREWAI = "crewai"
    LANGCHAIN = "langchain"

class TaskType(str, Enum):
    CODING = "coding"
    CONVERSATION = "conversation"
    AUTONOMOUS = "autonomous"
    COLLABORATION = "collaboration"
    RESEARCH = "research"
    SIMPLE = "simple"
```

### 4.2 Runtime Selection

```python
from app.core.runtime_selection import select_runtime_for_task

# Select runtime for execution
runtime = await select_runtime_for_task(
    goal="Refactor the auth module",
    capability="coding",
    tenant_id="tenant-123"
)

print(runtime.runtime_id)  # "claude_agent"
print(runtime.backend_provider)  # "anthropic"
print(runtime.backend_model)  # "claude-sonnet-4"
```

### 4.3 Working Memory

```python
from app.memory import get_working_memory

# Store working state
memory = get_working_memory()
await memory.set(
    thread_id="thread-123",
    state_data={"current_step": 5, "context": {...}},
    ttl_seconds=1800
)

# Retrieve
state = await memory.get(thread_id="thread-123")
```

### 4.4 Episodic Memory

```python
from app.memory import get_episodic_memory

# Store event
episodic = get_episodic_memory()
await episodic.store_event(
    thread_id="thread-123",
    tenant_id="tenant-123",
    event_type="tool_call",
    event_data={"tool": "search", "result": "..."}
)
```

### 4.5 Semantic Memory (Adapter)

```python
from app.memory import get_semantic_memory

# Store semantic memory
semantic = get_semantic_memory()
memory_id = await semantic.store(
    content_text="User prefers dark mode",
    tenant_id="tenant-123",
    memory_type="preference",
    source_type="user",
    source_id="user-123"
)

# Search
results = await semantic.search(
    query="user preferences",
    tenant_id="tenant-123"
)
```

---

## 5. How Pieces Map to Architecture

### 5.1 Runtime Architecture v2

| Architecture Concept | Implementation |
|---------------------|----------------|
| LangGraph orchestrator | Selected via runtime_type |
| OpenAI Agents SDK | `RuntimeType.OPENAI_AGENTS_SDK` |
| Claude Agent SDK | `RuntimeType.CLAUDE_AGENT_SDK` |
| Runtime registry | `WorkerRuntimeRegistry` in runtime_registry.py |
| Runtime selection | `RuntimeSelector` in runtime_selection.py |
| Task detection | `detect_task_type()` heuristics |

### 5.2 Memory Storage Decision

| Storage Layer | Implementation |
|--------------|----------------|
| Working memory | `WorkingMemoryStore` (Redis) |
| Episodic memory | `EpisodicMemoryStore` (Redis cache + Postgres) |
| Semantic memory | `SemanticMemoryStore` (SingleStore adapter) |
| Checkpoints | `CheckpointStore` (Postgres adapter) |
| Cortex briefs | `CortexStore` (Redis hot + Postgres) |

---

## 6. Environment Variables

### Runtime Selection

```bash
# Enable/disable
ENABLE_RUNTIME_SELECTION=true
ENABLE_RUNTIME_FALLBACK=true

# Allowed runtimes
ALLOWED_RUNTIMES=openai_agents,claude_agent,langchain
DEFAULT_RUNTIME_FALLBACK_ORDER=openai_agents,langchain

# Timeouts
RUNTIME_TIMEOUT_SECONDS=300
CHECKPOINT_INTERVAL_STEPS=50
```

### Memory/Storage

```bash
# Redis (required for working memory)
REDIS_URL=redis://localhost:6379

# SingleStore (for semantic - Phase 2)
# SINGLESTORE_URL=admin:password@host:3306/db

# Feature flags
MEMORY_WORKING_ENABLED=true
MEMORY_EPISODIC_ENABLED=true
MEMORY_SEMANTIC_ENABLED=false
MEMORY_CORTEX_ENABLED=false
```

---

## 7. Integration with Control Plane

### Existing Flow (Unchanged)

```
execution_request → policy_resolution → backend_selection → execution → usage_record
```

### New Flow (With Runtime)

```
execution_request 
    → RuntimeSelector.select_for_execution() [NEW]
        → detect_task_type(goal, capability)
        → select_runtime(task_type, tenant_id)
    → policy_resolution (unchanged)
    → backend_selection (uses runtime.backend_provider)
    → execution
    → usage_record (includes runtime_id) [EXTENDED]
```

### Key Points

1. **Runtime selection is NEW** - Before backend selection
2. **Control-plane entities UNCHANGED** - execution_request, policy_resolution, etc.
3. **Runtime provides backend context** - runtime.backend_provider maps to backend
4. **Audit trail extended** - runtime_id recorded in execution_history

---

## 8. What's NOT Included Yet

| What | Why Not |
|------|---------|
| Kafka | Not required for Phase 1 |
| Airflow | Not required - LangGraph handles orchestration |
| Camunda | Not required - existing workflow model sufficient |
| SingleStore client | Waiting for database provisioning |
| Production Redis setup | Placeholder for local dev |

---

## 9. Next Steps

### Phase 1 (Current)

- [x] Runtime registry with 5 runtimes
- [x] Task type detection
- [x] Runtime selection service
- [x] Working memory (Redis)
- [x] Episodic memory (Redis cache)
- [ ] Connect to actual Redis (requires Redis service)
- [ ] Test runtime selection

### Phase 2

- [ ] SingleStore provisioning
- [ ] Semantic memory adapter connection
- [ ] Checkpoint persistence to Postgres
- [ ] Cortex briefing full implementation
- [ ] Runtime health checks

### Phase 3

- [ ] OpenAI Agents SDK integration
- [ ] Claude Agent SDK worker implementation
- [ ] Runtime fallback chain execution
- [ ] Full LangGraph integration

---

## 10. Testing

```python
# Test runtime selection
from app.core.runtime_selection import select_runtime_for_task
from app.core.runtime_types import RuntimeType

async def test_runtime_selection():
    # Coding task
    runtime = await select_runtime_for_task(
        goal="Refactor the auth module",
        capability="coding",
        tenant_id="tenant-123"
    )
    assert runtime.runtime_id == "claude_agent"
    assert runtime.backend_provider == "anthropic"
    
    # Conversation task
    runtime = await select_runtime_for_task(
        goal="What tasks do I have?",
        capability=None,
        tenant_id="tenant-123"
    )
    assert runtime.runtime_id == "openai_agents"

# Test working memory
from app.memory import get_working_memory

async def test_working_memory():
    memory = get_working_memory()
    
    # Set
    await memory.set("thread-1", {"step": 1})
    
    # Get
    state = await memory.get("thread-1")
    assert state["step"] == 1
```

---

_End of Runtime & Memory Implementation_