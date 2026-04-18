# OpenAI Channel Runtime Implementation

This document describes the OpenAI Agents SDK integration as the human-facing channel runtime.

---

## 1. Overview

The OpenAI Channel Runtime provides human-facing conversation capability using OpenAI's Agents SDK. It is the default runtime for general conversation and integrates with the runtime selection system.

### Key Design Decisions

1. **Channel Runtime vs Backend**: This is a *channel* runtime, not a coding backend
2. **Durable Truth Outside**: Approval, delegation, and override logic remains in control-plane
3. **Adapter Pattern**: SDK can be swapped or disabled without breaking the interface
4. **Session Abstraction**: Sessions map to threads for workflow continuity

---

## 2. Architecture

### 2.1 Module Structure

```
app/runtime/
├── __init__.py           # Exports
├── types.py              # Type definitions
├── channel_runtime.py    # Abstract base
└── openai_channel_runtime.py  # OpenAI implementation
```

### 2.2 Class Hierarchy

```
ChannelRuntime (ABC)
    └── OpenAIChannelRuntime
    
ChannelResponse
Message
SessionContext
```

---

## 3. What Is Implemented

### 3.1 Core Types (`types.py`)

| Type | Status | Description |
|------|--------|-------------|
| `RuntimeType` | ✅ IMPLEMENTED | Runtime type enum |
| `TaskType` | ✅ IMPLEMENTED | Task category enum |
| `ChannelRuntimeType` | ✅ IMPLEMENTED | Channel type enum |
| `RuntimeCapability` | ✅ IMPLEMENTED | Capability model |
| `RuntimeStatus` | ✅ IMPLEMENTED | Health status enum |

### 3.2 Channel Abstraction (`channel_runtime.py`)

| Component | Status | Description |
|-----------|--------|-------------|
| `Message` | ✅ IMPLEMENTED | Message model |
| `SessionContext` | ✅ IMPLEMENTED | Session with history |
| `ChannelResponse` | ✅ IMPLEMENTED | Normalized response |
| `ChannelRuntime` | ✅ IMPLEMENTED | Abstract base class |

### 3.3 OpenAI Implementation (`openai_channel_runtime.py`)

| Method | Status | Description |
|--------|--------|-------------|
| `chat()` | ✅ ADAPTER | Message handling |
| `handle_tool_result()` | ✅ ADAPTER | Tool result handling |
| `create_session()` | ✅ IMPLEMENTED | Session creation |
| `get_session()` | 🔶 PLACEHOLDER | Would fetch from Redis |
| `health_check()` | ✅ IMPLEMENTED | Health status |

---

## 4. Usage

### 4.1 Creating a Session

```python
from app.runtime import get_channel_runtime, SessionContext

runtime = get_channel_runtime()

# Create session
session = await runtime.create_session(
    tenant_id="tenant-123",
    user_id="user-456",
    initial_context={"thread_id": "thread-789"}
)
```

### 4.2 Sending a Message

```python
# Send message
response = await runtime.chat(session, "Hello, help me with coding")

print(response.message)
print(f"Tokens used: {response.tokens_used}")
print(f"Latency: {response.latency_ms}ms")
```

### 4.3 Handling Tool Results

```python
# After tool executes
response = await runtime.handle_tool_result(
    session,
    tool_call_id="call_123",
    tool_result={"status": "success", "data": "..."}
)
```

---

## 5. Configuration

### Environment Variables

```bash
# OpenAI Channel Runtime
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_CHANNEL_MODEL=gpt-4o
OPENAI_CHANNEL_INSTRUCTIONS=You are Autonomyx...
```

### Config Structure

```python
config = {
    "api_key": "sk-...",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-4o",
    "instructions": "You are Autonomyx...",
    "tools": [...],  # Available tools
    "mcp_servers": [...],  # MCP server configs
}
```

---

## 6. Integration with Runtime Selection

The OpenAI channel runtime integrates with the existing runtime registry:

```python
from app.core.runtime_registry import get_runtime_registry

registry = get_runtime_registry()

# Register channel runtime capability
registry.register_capability(
    runtime_id="openai_agents",
    capability="channel",
    handler=get_channel_runtime()
)
```

### Runtime Mapping

| Task Type | Channel Runtime | Notes |
|-----------|-----------------|-------|
| conversation | openai_agents | Default for chat |
| coding | claude_coder | Uses coding backend |
| research | openai_agents | Uses research backend |

---

## 7. What Is Placeholder

| Component | Status | Notes |
|-----------|--------|-------|
| SDK Integration | 🔶 ADAPTER | Requires `openai` package |
| Session Persistence | 🔶 PLACEHOLDER | Would use Redis |
| Tool Registry | 🔶 PLACEHOLDER | Would load from config |
| MCP Servers | 🔶 PLACEHOLDER | Config only |
| Handoff Logic | 🔶 PLACEHOLDER | Would integrate with control-plane |

---

## 8. Next Steps

### Phase 2 - Full Integration

- [ ] Install `openai` package with agents support
- [ ] Implement actual SDK calls
- [ ] Add session persistence with Redis
- [ ] Connect tool registry
- [ ] Add MCP server support

### Phase 3 - Production

- [ ] Add rate limiting
- [ ] Add monitoring/observability
- [ ] Add session encryption
- [ ] Implement handoff to control-plane

---

## 9. API Reference

```python
from app.runtime import (
    get_channel_runtime,
    SessionContext,
    ChannelResponse,
)

# Get runtime
runtime = get_channel_runtime()

# Health check
health = await runtime.health_check()
print(health)

# Session management
session = await runtime.get_session(session_id)
if not session:
    session = await runtime.create_session(tenant_id)

# Chat
response = await runtime.chat(session, "Hello!")
```

---

_End of OpenAI Channel Runtime Implementation_