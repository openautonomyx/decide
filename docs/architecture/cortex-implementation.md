# Cortex & Compaction Implementation

This document describes the Cortex memory and compaction implementation for Runtime Architecture v2.

---

## 1. What Is Implemented

### 1.1 Memory Types (`app/memory/types.py`)

| Type | Status | Description |
|------|--------|-------------|
| `MemoryType` | ✅ IMPLEMENTED | Enum (working, episodic, semantic, cortex, checkpoint) |
| `CortexCategory` | ✅ IMPLEMENTED | 12 typed categories (fact, preference, decision, etc.) |
| `TypedMemory` | ✅ IMPLEMENTED | Typed memory entry |
| `CompactionSummary` | ✅ IMPLEMENTED | Compaction/briefing summary |

### 1.2 Compaction Service (`app/memory/compaction.py`)

| Method | Status | Description |
|--------|--------|-------------|
| `estimate_tokens()` | ✅ IMPLEMENTED | Token estimation |
| `should_compact()` | ✅ IMPLEMENTED | Budget-based trigger |
| `should_checkpoint()` | ✅ IMPLEMENTED | Step-based trigger |
| `generate_summary()` | ✅ IMPLEMENTED | Summary generation |
| `extract_typed_memories()` | ✅ IMPLEMENTED | Category extraction |

---

## 2. Typed Memory Categories

### Category List

| Category | Description | Source |
|----------|-------------|--------|
| FACT | Verified facts | System, workflow |
| PREFERENCE | User/org preferences | User, profile |
| DECISION | Decisions made | Agent, workflow |
| IDENTITY | Identity info | User, employee |
| EVENT | Important events | System |
| OBSERVATION | Observations | Agent |
| GOAL | Goals/milestones | Workflow |
| TODO | Todos | Workflow |
| CONSTRAINT | Constraints/rules | Policy, workflow |
| APPROVAL | Approval records | Control plane |
| OVERRIDE | Override records | Control plane |
| DELEGATION | Delegation records | Control plane |
| MILESTONE | Milestone progress | Workflow |

---

## 3. How Compaction Works

### 3.1 Context Budget

```python
from app.memory.compaction import CONTEXT_BUDGETS

# Default budgets
CONTEXT_BUDGETS = {
    "coding": {"input": 150000, "output": 50000},
    "conversation": {"input": 50000, "output": 10000},
    "autonomous": {"input": 200000, "output": 100000},
    "collaboration": {"input": 100000, "output": 50000},
    "simple": {"input": 30000, "output": 5000},
}
```

### 3.2 Trigger Logic

```python
from app.memory import get_compaction_service

service = get_compaction_service()

# Check if compaction needed
should_compact = service.should_compact(
    task_type="coding",
    messages=message_history,
    current_tokens=100000
)

# Should trigger at 80% of budget
# 150000 * 0.8 = 120000 tokens
```

### 3.3 Summary Generation

```python
summary = await service.generate_summary(
    thread_id="thread-123",
    tenant_id="tenant-123",
    task_type="coding",
    messages=message_history,
    goals=["implement auth", "add tests"],
    constraints=["must use OAuth", "no secrets in code"],
    preferences=["prefer dark mode"]
)

print(summary.running_summary)   # Summary of recent messages
print(summary.open_loops)          # ["implement auth", "add tests"]
print(summary.tokens_before)       # 45000
print(summary.tokens_after)       # 2500
```

---

## 4. Integration with Memory Layers

### 4.1 Memory Storage Map

| Layer | Storage | When |
|-------|---------|------|
| Working | Redis | Fast session state |
| Episodic | Redis cache + Postgres | Event history |
| Semantic | SingleStore | Knowledge |
| Checkpoint | Postgres | Durable recovery |
| Cortex | Redis hot + Postgres | Briefs |

### 4.2 Compaction Integration

```python
# In LangGraph node
async def check_and_compact(state):
    service = get_compaction_service()
    
    # Check budget
    if service.should_compact(state.task_type, state.messages, state.current_tokens):
        # Generate summary
        summary = await service.generate_summary(...)
        
        # Store in cortex
        cortex = get_cortex_store()
        await cortex.create_briefing(
            thread_id=state.thread_id,
            summary=summary.running_summary,
            pending_actions=summary.open_loops
        )
        
        # Clear messages, keep summary
        state.messages = [{"role": "system", "content": summary.running_summary}]
    
    return state
```

---

## 5. What Is Placeholder

| Component | Status | Notes |
|-----------|--------|-------|
| Token estimation | ⚠️ APPROXIMATE | ~4 chars per token |
| Category extraction | ⚠️ HEURISTIC | Simple keyword matching |
| Postgres persistence | 🔶 ADAPTER | Uses existing tables |
| SingleStore integration | 🔶 ADAPTER | Waiting for DB |
| Redis connection | 🔶 READY | Available if Redis runs |

---

## 6. Next Steps

### Phase 2 (After Provisioning)

- [ ] Connect SingleStore client
- [ ] Implement Postgres persistence
- [ ] Add embedding generation
- [ ] Improve category extraction with LLM

### Phase 3 (Production)

- [ ] Token counting with actual tokenizer
- [ ] Checkpoint encryption
- [ ] Rate limiting
- [ ] Monitoring

---

## 7. API Reference

```python
from app.memory import (
    get_compaction_service,
    get_cortex_store,
    CortexCategory,
)

# Compaction service
service = get_compaction_service()
budget = service.get_context_budget("coding")
should = service.should_compact("coding", messages, 100000)

# Generate summary
summary = await service.generate_summary(...)

# Extract typed memories
memories = await service.extract_typed_memories(...)

# Cortex store
cortex = get_cortex_store()
briefing = await cortex.get_briefing(thread_id)
```

---

_End of Cortex Implementation_