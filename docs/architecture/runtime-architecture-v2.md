# Runtime Architecture v2

This document describes Runtime Architecture v2, which adds LangGraph as the top-level orchestration backbone while preserving all existing Autonomyx concepts, entities, and control-plane model.

---

## 1. Purpose of Runtime v2

Runtime v2 exists to:

1. **Enable complex multi-step orchestration** - Single-agent runtimes cannot handle branching workflows, parallel execution, human-in-the-loop checkpoints, or long-running autonomous tasks
2. **Support multiple worker runtimes** - Different tasks require different runtime capabilities; no single runtime fits all use cases
3. **Preserve human oversight** - Approvals, overrides, delegation, RBAC, and audit must remain first-class, not bypassed by agent autonomy
4. **Maintain vendor portability** - Runtime selection should be configurable per tenant, not hardcoded

### What Changed from v1

| Aspect | v1 (Original) | v2 (New) |
|--------|--------------|----------|
| Orchestration | Implicit (single backend call) | LangGraph workflow graph |
| Human-facing | Single agent | OpenAI Agents SDK channel |
| Worker selection | Single backend | Runtime registry with selection policy |
| Memory | Ad-hoc checkpoints | Cortex layer with typed taxonomy |
| Long-running | Not supported | Deep Agents / CrewAI support |

---

## 2. What Remains Unchanged

The following are preserved in full and **must not be modified or bypassed** by any runtime:

### Core Entity Split
- **Employee** = Human entity (never merged with Agent)
- **Agent** = AI entity (separate IDs and tables)

### Collaboration Containers
- **Product** = Persistent business function
- **Project** = Short-term execution
- **Group** = Community/interest

### Workflow Entities
- Task (atomic unit)
- Task dependency
- Task assignment history
- Deadline (separate from task end)
- Milestone
- Reminder
- Escalation

### Control Plane Entities
- execution_request
- execution_history
- policy_resolution
- decision_record
- override_record
- approval_request (human approval distinct from rule decision)
- backend_selection
- fallback_event
- responsibility_assignment (delegation vs acting vs ownership transfer)
- usage_record
- memory_checkpoint
- tenant_policy

### Governance
- RBAC (role-based access control)
- Audit logging (full trace)
- Tenant policy resolution

---

## 3. Major Runtime Decisions

### 3.1 LangGraph as Orchestrator

**LangGraph** is the top-level orchestrator for all runtime execution. It manages:

- Workflow graph definition and execution
- State management across steps
- Conditional branching based on policy evaluation
- Human-in-the-loop checkpoints (pausing for approval)
- Parallel execution for independent branches
- Error handling and retry policies
- Memory checkpoint coordination

```python
# Example: LangGraph workflow for execution_request
from langgraph.graph import StateGraph, END

class ExecutionState(TypedDict):
    execution_request_id: str
    tenant_id: str
    goal: str
    policy_resolution: dict | None
    approval_status: str | None
    backend_selected: str | None
    result: dict | None
    history: list[dict]

graph = StateGraph(ExecutionState)
graph.add_node("evaluate_policy", evaluate_policy)
graph.add_node("check_approval", check_approval)
graph.add_node("select_backend", select_backend)
graph.add_node("execute", execute_worker)
graph.add_node("checkpoint", write_checkpoint)

graph.set_entry_point("evaluate_policy")
graph.add_edge("evaluate_policy", "check_approval")
graph.add_conditional_edges(
    "check_approval",
    lambda s: "select_backend" if s["approval_status"] == "auto" else "await_approval",
    {"select_backend": "select_backend", "await_approval": END}
)
graph.add_edge("select_backend", "execute")
graph.add_edge("execute", "checkpoint")
graph.add_edge("checkpoint", END)

compiled = graph.compile()
```

### 3.2 OpenAI Agents SDK as Human-Facing Runtime

**OpenAI Agents SDK** is the default runtime for human-facing conversation:

- Natural language interface for employees
- Multi-turn conversation support
- Built-in tool/function calling
- MCP (Model Context Protocol) integration
- **Not** the source of truth for workflow state (LangGraph holds state)

```python
# Human-facing agent using OpenAI Agents SDK
from openai import agents

agent = agents.Agent(
    name="autonomyx_assistant",
    instructions="You are Autonomyx, an AI assistant....",
    tools=[search_knowledge_base, create_task, check_approvals],
    mcp_servers=["memory-service", "task-service"]
)
```

### 3.3 Runtime Selection Policy

A tenant-configurable policy determines which runtime executes which request:

```python
from enum import Enum

class RuntimeType(Enum):
    LANGGRAPH_ORCHESTRATOR = "langgraph"      # Top-level orchestrator
    OPENAI_AGENTS_SDK = "openai_agents"      # Human-facing
    CLAUDE_AGENT_SDK = "claude_agent"       # Premium coding/research
    DEEP_AGENTS = "deep_agents"            # Long-running autonomous
    CREWAI = "crewai"                     # Flat collaborative team
    LANGCHAIN = "langchain"               # Lightweight/simple

RUNTIME_SELECTION_POLICY = """
# Runtime selection policy (tenant-configurable)
coding:
  preferred: claude_agent
  fallback: langchain
  reason: Premium coding requires strong reasoning

general_conversation:
  preferred: openai_agents
  fallback: langchain
  reason: Human-facing interaction needs OpenAI SDK

long_running_autonomous:
  preferred: deep_agents
  fallback: crewai
  reason: Hours-long execution, multiple tools

flat_collaboration:
  preferred: crewai
  fallback: langchain
  reason: Volunteer/student/NGO teamwork

lightweight_task:
  preferred: langchain
  fallback: none
  reason: Simple retrieval or transformation
"""
```

---

## 4. Channel Runtime

**Channel runtime** handles communication between human employees and the Autonomyx system.

### Definition
A Channel is a first-class entity (existing schema) with a runtime adapter:

```python
class ChannelRuntime(Protocol):
    """Protocol for channel adapters"""
    async def send_message(self, channel_id: str, message: Message) -> None: ...
    async def receive_message(self, channel_id: str) -> Message | None: ...
    async def list_messages(self, channel_id: str, limit: int) -> list[Message]: ...

# Channel types map to runtime behavior
CHANNEL_RUNTIME_MAP = {
    "slack": SlackChannelRuntime,      # Uses OpenAI Agents SDK
    "discord": DiscordChannelRuntime, # Uses OpenAI Agents SDK
    "email": EmailChannelRuntime,    # Uses LangChain (simple)
    "webhook":WebhookChannelRuntime, # Uses LangChain (simple)
    "api": APIChannelRuntime,       # Uses OpenAI Agents SDK
}
```

### Channel Profile Link
- channel_profile_master → defines channel runtime settings
- agent_governance_profile → links to allowed runtimes per agent

---

## 5. Branch Runtime

**Branch runtime** handles parallel execution branches within a LangGraph workflow.

### Use Cases
- Multiple independent subtasks can run in parallel
- A/B testing different worker runtimes
- Fallback chain when primary fails

```python
# Branch runtime example in LangGraph
from langgraph.graph import Branch

# Parallel branch: search in multiple backends simultaneously
graph.add_node("search_claude", lambda s: search(s, runtime="claude_agent"))
graph.add_node("search_devstral", lambda s: search(s, runtime="devstral"))
graph.add_node("search_lamapi", lambda s: search(s, runtime="langchain"))

# Branch execution
graph.add_branch(
    "search",
    {
        "search_claude": "search_claude",
        "search_devstral": "search_devstral", 
        "search_lamapi": "search_lamapi"
    }
)

# Join results
graph.add_node("merge_results", merge_search_results)
```

### Branch Types
| Type | Description |
|------|-------------|
| parallel | All branches execute simultaneously |
| failover | Try branch N+1 if N fails |
| a_b_test | Compare results from different runtimes |

---

## 6. Worker Runtime Registry

**Worker runtime registry** maintains available runtimes and their capabilities.

### Registry Schema (existing table extended)

```sql
-- Extend existing worker_registry or create new
CREATE TABLE worker_runtime (
    runtime_id VARCHAR(36) PRIMARY KEY,
    runtime_type VARCHAR(50) NOT NULL,  -- See RuntimeType enum
    backend_provider VARCHAR(50),         -- openai, anthropic, etc.
    backend_model VARCHAR(100),
    endpoint_url VARCHAR(500),
    config JSONB,                        -- Runtime-specific config
    capabilities JSONB,                 -- What this runtime supports
    cost_per_1k_input NUMERIC(10, 6),
    cost_per_1k_output NUMERIC(10, 6),
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Runtime capability taxonomy
-- {"tags": ["coding", "research", "conversation", "autonomous"]}
-- {"max_context_tokens": 200000}
-- {"supports_streaming": true}
-- {"supports_tools": true}
```

### Registry Usage in Control Plane

```python
class WorkerRuntimeRegistry:
    def __init__(self):
        self.runtimes: dict[str, WorkerRuntime] = {}
    
    async def select_runtime(
        self, 
        task_type: str,
        quality: str,
        tenant_id: str,
        policy: dict
    ) -> WorkerRuntime:
        # Load tenant policy for runtime selection
        tenant_policy = await self.get_tenant_policy(tenant_id)
        
        # Evaluate policy rules
        for rule in tenant_policy.runtime_selection_rules:
            if self.matches(task_type, quality, rule):
                return self.get_runtime(rule.preferred)
        
        # Fallback to default
        return self.get_default_runtime(task_type)
    
    def get_default_runtime(self, task_type: str) -> WorkerRuntime:
        defaults = {
            "coding": "claude_agent",
            "conversation": "openai_agents", 
            "autonomous": "deep_agents",
            "collaboration": "crewai",
            "simple": "langchain"
        }
        return self.runtimes.get(defaults.get(task_type, "langchain"))
```

---

## 7. Cortex Memory Layer

**Cortex** is the memory layer that persists state across LangGraph executions.

### Memory Type Taxonomy

| Type | Retention | Purpose |
|------|-----------|---------|
| **episodic** | Per-execution | Individual execution history |
| **semantic** | Long-term | Shared knowledge across executions |
| **working** | Per-step | Current workflow state |
| **checkpoint** | Periodic | Long-running recovery points |

### Schema (existing table extended)

```sql
-- Extend existing memory_checkpoint
CREATE TABLE cortex_memory (
    memory_id VARCHAR(36) PRIMARY KEY,
    memory_type VARCHAR(20) NOT NULL,  -- episodic, semantic, working, checkpoint
    tenant_id VARCHAR(36) REFERENCES tenant(id),
    execution_request_id VARCHAR(36) REFERENCES execution_request(id),
    thread_id VARCHAR(36),           -- LangGraph thread
    
    -- Content
    content_data JSONB NOT NULL,      -- Actual memory content
    embedding VECTOR(1536),         -- For semantic search
    
    -- Metadata
    created_by_type VARCHAR(20),    -- employee, agent, system
    created_by_id VARCHAR(36),
    expires_at TIMESTAMP,
    
    -- Checkpoint metadata (for long-running recovery)
    checkpoint_step INTEGER,
    checkpoint_hash VARCHAR(64),
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for semantic search
CREATE INDEX idx_cortex_semantic_vec 
ON cortex_memory USING ivfflat (embedding vector_cosine_ops)
WHERE memory_type = 'semantic';
```

### Cortex API

```python
class CortexMemory:
    async def store_episodic(
        self, 
        execution_id: str, 
        events: list[dict]
    ):
        await self.db.execute("""
            INSERT INTO cortex_memory (memory_id, memory_type, execution_request_id, content_data)
            VALUES (%s, 'episodic', %s, %s)
        """, [uuid4(), execution_id, json.dumps(events)])
    
    async def query_semantic(
        self, 
        query: str, 
        tenant_id: str,
        limit: int = 10
    ) -> list[dict]:
        # Embed query and search
        query_embedding = await self.embed(query)
        return await self.db.query("""
            SELECT content_data 
            FROM cortex_memory 
            WHERE memory_type = 'semantic' 
            AND tenant_id = %s
            ORDER BY embedding <=> %s
            LIMIT %s
        """, [tenant_id, query_embedding, limit])
    
    async def get_checkpoint(
        self, 
        thread_id: str, 
        step: int | None = None
    ) -> dict | None:
        # Recover from checkpoint for long-running execution
        if step:
            return await self.db.query("""
                SELECT content_data FROM cortex_memory
                WHERE memory_type = 'checkpoint'
                AND thread_id = %s
                AND checkpoint_step = %s
            """, [thread_id, step])
        else:
            # Get latest
            return await self.db.query("""
                SELECT content_data FROM cortex_memory
                WHERE memory_type = 'checkpoint'
                AND thread_id = %s
                ORDER BY checkpoint_step DESC
                LIMIT 1
            """, [thread_id])
```

---

## 8. Compaction Checkpoint Policy

**Compaction** consolidates memory checkpoints to prevent unbounded growth.

### Policy Configuration

```python
COMPACTION_POLICY = """
# Compaction checkpoint policy (tenant-configurable)

checkpoints:
  frequency: every_50_steps        # Write checkpoint every N steps
  max_retention: 7_days         # Delete after N days (unless flagged)
  compression: gzip            # Compress old checkpoints
  
semantic:
  dedup_window: 24_hours     # Deduplicate within time window
  similarity_threshold: 0.95  # Merge above threshold
  max_per_execution: 100       # Cap memories per execution
  
episodic:
  retention: 30_days        # Keep execution history
  aggregation: summarize    # Summarize old episodes vs delete
  
checkpoint_recovery:
  retry_from_last: true        # On failure, retry from last checkpoint
  max_retry_steps: 10        # Limit retry attempts
"""
```

### Implementation

```python
class CompactionService:
    async def compact_checkpoint(
        self, 
        thread_id: str, 
        policy: CompactionPolicy
    ):
        # Get all checkpoints for thread
        checkpoints = await self.db.query("""
            SELECT memory_id, checkpoint_step, created_at
            FROM cortex_memory
            WHERE memory_type = 'checkpoint'
            AND thread_id = %s
            ORDER BY checkpoint_step DESC
        """, [thread_id])
        
        # Keep only N most recent
        to_delete = checkpoints[policy.max_checkpoints:]
        for ckpt in to_delete:
            # Compress instead of delete
            await self.compress_checkpoint(ckpt.memory_id)
            await self.db.execute("""
                UPDATE cortex_memory 
                SET memory_type = 'checkpoint_compressed'
                WHERE memory_id = %s
            """, [ckpt.memory_id])
```

---

## 9. Context Budget Policy

**Context budget** limits token usage per execution/request.

### Budget Allocation

```python
CONTEXT_BUDGET_POLICY = """
# Context budget policy (tenant-configurable)

budgets:
  coding:
    input_tokens: 150000      # ~150k context
    output_tokens: 50000
    reasoning_effort: high
    
  general_conversation:
    input_tokens: 50000
    output_tokens: 10000  
    reasoning_effort: medium
    
  long_running:
    input_tokens: 200000      # Larger for autonomous
    output_tokens: 100000
    checkpoint_every: 50
    
priority_threshold:
  # If remaining budget < threshold, fail fast
  input: 5000
  output: 2000
"""
```

### Enforcement in LangGraph

```python
class ContextBudgetMiddleware:
    def __init__(self, policy: ContextBudgetPolicy):
        self.policy = policy
    
    async def __call__(self, state: ExecutionState):
        task_type = state.get("task_type", "general")
        budget = self.policy.budgets.get(task_type)
        
        # Track usage
        current_input = state.get("input_token_count", 0)
        current_output = state.get("output_token_count", 0)
        
        if current_input > budget.input_tokens:
            raise ContextBudgetExceeded(
                f"Input tokens {current_input} exceeded budget {budget.input_tokens}"
            )
        
        if current_output > budget.output_tokens:
            raise ContextBudgetExceeded(
                f"Output tokens {current_output} exceeded budget {budget.output_tokens}"
            )
        
        return state
```

---

## 10. Briefing Generation Flow

**Briefing** generates contextual summaries for human reviewers.

### Flow

```
execution_request → policy_resolution → [if approval needed] 
    → pause_for_approval → [on approve] 
        → generate_briefing → checkpoint → execute
```

### Briefing Generation

```python
async def generate_briefing(
    execution_request_id: str,
    target audience: str  # employee, manager, customer
) -> Briefing:
    # Gather context
    exec_req = await db.get_execution_request(execution_request_id)
    history = await db.get_execution_history(execution_request_id)
    policy = await db.get_policy_resolution(execution_request_id)
    approval = await db.get_approval_request(execution_request_id)
    
    # Generate summary based on audience
    if audience == "employee":
        summary = f"Your request '{exec_req.goal}' has been approved."
        details = format_for_employee(history, policy)
    elif audience == "manager":
        summary = f"Request from {exec_req.tenant_id} requires approval."
        details = format_for_manager(history, policy, approval)
    
    return Briefing(
        summary=summary,
        details=details,
        recommendations=get_recommendations(policy),
        risk_factors=get_risks(policy)
    )
```

### Briefing Integration with Approval

```python
# LangGraph node for approval briefing
async def generate_approval_briefing(state: ExecutionState) -> ExecutionState:
    briefing = await generate_briefing(
        state["execution_request_id"],
        audience="manager"
    )
    
    # Send to approval channel
    await channel.send_message(
        channel_id=state["approval_channel_id"],
        message=briefing.to_message()
    )
    
    return {**state, "briefing_sent": True}
```

---

## 11. Mapping to Current Entities

### Existing Schema Integration

| Current Entity | v2 Runtime Role |
|----------------|-----------------|
| execution_request | LangGraph workflow input |
| execution_history | Cortex episodic memory |
| memory_checkpoint | Cortex checkpoint memory |
| backend_selection | Runtime registry lookup |
| fallback_event | Branch runtime failover |
| approval_request | LangGraph pause + briefing |
| usage_record | Cost tracking per runtime |
| channel_profile_master | Channel runtime config |
| agent_governance_profile | Runtime capability filter |

### Control Plane Preservation

All existing control-plane entities remain unchanged:

```python
# These are NEVER bypassed by any runtime
CONTROL_PLANE_ENTITIES = [
    "execution_request",      # Always created first
    "policy_resolution",     # Always evaluated
    "decision_record",        # Rule decisions preserved
    "override_record",      # Human overrides preserved
    "approval_request",     # Human approval preserved  
    "responsibility_assignment",  # Delegation preserved
    "usage_record",          # Cost tracking preserved
]

# Runtime reads from these but CANNOT modify
CONTROL_PLANE_READ_ONLY = [
    "tenant_policy",
    "employee",
    "agent", 
    "product",
    "project",
    "group",
    "task",
]
```

---

## 12. Open Implementation Questions

### Questions Requiring Resolution

| Question | Impact | Priority |
|----------|--------|----------|
| How to handle runtime-specific failures vs policy failures? | Error handling design | High |
| Should runtime selection be visible in execution trace? | Audit completeness | High |
| How to cost-allocate multi-runtime executions? | Billing model | Medium |
| Can runtime be changed mid-execution (reroute)? | Control plane integrity | High |
| How to test runtime selection policy? | Testing strategy | Medium |
| MCP server failures - propagate or handle? | Reliability design | Medium |
| Long-running checkpoint encryption at rest? | Security model | High |

### Known Gaps

1. **Runtime health monitoring** - Need per-runtime health checks
2. **A/B testing framework** - Not yet designed
3. **Cost allocation per runtime** - UsageRecord needs runtime_id
4. **Runtime capability discovery** - Not dynamic

---

## 13. Migration / Rollout Strategy from Current Runtime

### Phase 1: Foundation
- Add worker_runtime registry
- Add Cortex memory layer (separate tables)
- No behavior change yet

### Phase 2: Runtime Registry
- Add runtime selection policy to tenant_policy
- Add runtime_id to usage_record
- Implement registry lookup

### Phase 3: LangGraph Integration
- Add LangGraph as orchestration layer
- Map existing control-plane flow to LangGraph nodes
- Preserve all existing entities

### Phase 4: Channel Runtime
- Add channel runtime adapters
- Connect to channel_profile_master

### Phase 5: Full Migration
- Enable v2 runtime by default
- Keep v1 as fallback
- Deprecate v1 after validation

### Rollback Plan
- Each phase is reversible
- v1 runtime remains available as fallback
- Feature flags disable v2 components

---

## Appendix A: Runtime Selection Examples

### Coding Task → Claude Agent SDK

```
Request: "Refactor the authentication module for better error handling"

Runtime Selection:
1. task_type = "coding" (detected from goal)
2. policy looks up coding rule
3. preferred = "claude_agent"
4. LangGraph loads Claude Agent SDK worker
5. Execution proceeds
```

### General Conversation → OpenAI Agents SDK

```
Request: "What tasks do I have due this week?"

Runtime Selection:
1. task_type = "conversation"  
2. policy looks up conversation rule
3. preferred = "openai_agents"
4. LangGraph loads OpenAI Agents SDK channel
5. Multi-turn conversation proceeds
```

### Long-Running Autonomous → Deep Agents

```
Request: "Research the entire literature on topic X and create a summary"

Runtime Selection:
1. task_type = "autonomous" (detected from scope)
2. policy looks up long_running rule
3. preferred = "deep_agents"
4. LangGraph loads Deep Agents worker with checkpoint
5. Hours-long execution with periodic checkpoints
```

### Volunteer Team → CrewAI

```
Request: "Collaborate with the research team to analyze this dataset"

Runtime Selection:
1. task_type = "collaboration" (detected from context)
2. tenant = volunteer_student_org
3. policy maps to "crewai"
4. LangGraph loads CrewAI with flat team structure
5. Multiple agents collaborate without hierarchy
```

### Simple Task → LangChain

```
Request: "What is my current quota?"

Runtime Selection:  
1. task_type = "simple" (detected from simplicity)
2. policy looks up lightweight rule
3. preferred = "langchain"
4. LangGraph loads LangChain lightweight worker
5. Fast execution, minimal state
```

---

## Appendix B: Runtime Capability Matrix

| Capability | OpenAI Agents | Claude Agent | Deep Agents | CrewAI | LangChain |
|------------|----------------|-------------|-------------|--------|-----------|
| Multi-turn chat | ✅ | ❌ | ❌ | ✅ | ❌ |
| Tool use | ✅ | ✅ | ✅ | ✅ | ✅ |
| Coding | ⚠️ | ✅ | ⚠️ | ⚠️ | ❌ |
| Long-running | ❌ | ❌ | ✅ | ⚠️ | ❌ |
| Checkpoint | ❌ | ✅ | ✅ | ⚠️ | ❌ |
| Parallel exec | ❌ | ❌ | ✅ | ✅ | ❌ |
| MCP support | ✅ | ❌ | ❌ | ❌ | ⚠️ |
| Human-in-loop | ✅ | ❌ | ✅ | ⚠️ | ❌ |

---

_End of Runtime Architecture v2_