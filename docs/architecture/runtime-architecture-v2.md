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
# Example: LangGraph workflow using Canonical State Schema (v2.1)
from langgraph.graph import StateGraph, END

# Use the canonical ExecutionState from section 3.1.1 above
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
    lambda s: "select_backend" if s.get("approval_status") == "auto" else "await_approval",
    {"select_backend": "select_backend", "await_approval": END}
)
graph.add_edge("select_backend", "execute")
graph.add_edge("execute", "checkpoint")
graph.add_edge("checkpoint", END)

compiled = graph.compile()
```

### 3.1.1 Canonical State Schema (v2.1)

The following defines the canonical state schema organized into 10 families with clear separation between **config**, **runtime state**, **decision state**, and **outcome state**.

**Layer Distinctions:**
- **Config**: What was set ahead of time
- **Runtime State**: What was true during execution
- **Decision State**: What was chosen and why
- **Outcome State**: What happened afterward

```python
from typing import TypedDict
from typing_extensions import NotRequired

class ExecutionState(TypedDict):
    """
    Canonical execution state machine with 10 families.
    Preserves all v2 fields while adding structured organization.
    """
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FAMILY 1: IDENTITY, GOAL, AND AUTHORITY
    # Who is acting, for what goal, with what authority
    # ═══════════════════════════════════════════════════════════════════════════
    
    ## Config (set ahead of time)
    user_id: str                          # Who initiated the request
    tenant_id: str                       # Tenant context
    user_expertise: str                 # beginner, intermediate, expert
    
    ## Runtime State (observed/derived)
    intent_clarity: str                  # clear, ambiguous, unclear
    goal: str                           # The goal being pursued
    goal_id: NotRequired[str]           # Goal identifier
    goal_type: NotRequired[str]        # Type: task, query, exploration
    
    ## Decision State (chosen)
    auth_context: NotRequired[dict]     # Authorization context
    approval_pattern: NotRequired[str]  # auto, manual, escalation
    
    ## Missing Fields (added)
    boundary_clarity: NotRequired[str]   # clear, ambiguous, unclear
    clarification_required: NotRequired[bool]
    clarification_status: NotRequired[str]  # none, pending, answered
    
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FAMILY 2: RUNTIME AND EXECUTION ENVIRONMENT
    # Where and how execution happens
    # ═══════════════════════════════════════════════════════════════════════════
    
    ## Config
    runtime: str                         # langgraph, openai_agents, claude_agent
    os: NotRequired[str]                # Operating system
    sandbox_mode: NotRequired[str]      # full, restricted, none
    timeout_settings: NotRequired[dict]
    
    ## Runtime State
    network_access: bool                  # Is network available
    installed_tools: list[str]          # List of available tools
    concurrent_usage: NotRequired[int] # Current concurrent usage
    api_availability: NotRequired[dict] # API status
    
    ## Missing Fields (added)
    execution_mode: NotRequired[str]    # sync, async
    background_allowed: NotRequired[bool]
    checkpointing_required: NotRequired[bool]
    human_interruptibility: NotRequired[bool]
    
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FAMILY 3: MODEL, PROVIDER, AND CAPABILITIES
    # What model stack is available
    # ═══════════════════════════════════════════════════════════════════════════
    
    ## Config (static capability - what model CAN do)
    provider: str                       # openai, anthropic, etc.
    model_variant: str                  # Specific model
    llm_version: NotRequired[str]
    modality: NotRequired[str]          # text, multimodal
    tool_calling: bool                  # Model supports tool calling
    structured_output: bool             # Model supports structured output
    streaming: bool                    # Model supports streaming
    code_execution: bool                # Model supports code execution
    web_search: bool                   # Model supports web search
    file_handling: bool                # Model supports file handling
    context_window: int                # Configured context window size
    
    ## Runtime State (dynamic usage - what model IS using)
    context_window_usage: NotRequired[dict]  # {input: int, output: int, total: int}
    tokens_input: NotRequired[int]     # Actual tokens used (input)
    tokens_output: NotRequired[int]    # Actual tokens used (output)
    
    ## Missing Fields (added)
    pricing: NotRequired[dict]          # {input_cost_per_1k: float, output_cost_per_1k: float}
    rate_limits: NotRequired[dict]     # Rate limit configuration
    
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FAMILY 4: ROUTING, PLANNING, AND ORCHESTRATION
    # How execution choices are made
    # ═══════════════════════════════════════════════════════════════════════════
    
    ## Config
    agent_type: NotRequired[str]        # Types: agent, assistant, coordinator
    delegation_depth: NotRequired[int] # How deep delegation goes
    planning_mode: NotRequired[str]     # explicit, implicit, none
    quality_threshold: NotRequired[float]
    cost_budget: NotRequired[float]
    
    ## Decision State (runtime decisions - what model CHOSE to do)
    routing_strategy: NotRequired[str]     # Strategy used for routing
    tool_selection: NotRequired[list[str]]  # Tools selected for execution
    routed_model: NotRequired[str]       # Model selected for routing
    fallback_chain: NotRequired[list[str]]  # Fallback chain (DUPLICATE REMOVED: keep only here)
    retry_strategy: NotRequired[str]     # Retry strategy
    
    ## Missing Fields (added)
    decision_type: NotRequired[str]     # Type of decision made
    rationale_trace: NotRequired[list[str]]  # Why decisions were made
    
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FAMILY 5: SKILL, PROMPT, AND TOOLING LAYER
    # Reusable operational capability pack
    # ═══════════════════════════════════════════════════════════════════════════
    
    ## Config (static - what was configured)
    skill: NotRequired[str]             # Skill being used
    skill_version: NotRequired[str]        # Skill version (DUPLICATE REMOVED: keep only here)
    prompt: NotRequired[str]            # Current prompt
    system_prompt: NotRequired[str]    # System prompt
    thinking_mode: NotRequired[str]    # Chain of thought mode
    
    ## Runtime State
    tools: list[str]                   # Tools available
    mcp_servers: NotRequired[list[str]] # MCP servers (DUPLICATE REMOVED: keep only here)
    mcp_servers_connected: NotRequired[list[str]]  # Connected MCP servers
    reference_docs_loaded: NotRequired[list[str]]
    bundled_scripts: NotRequired[list[str]]
    
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FAMILY 6: DATA, KNOWLEDGE, AND RETRIEVAL
    # What information the system can draw from
    # ═══════════════════════════════════════════════════════════════════════════
    
    ## Config
    schema: NotRequired[dict]            # Data schema
    rag_data_sources: NotRequired[list[str]]  # RAG data sources
    vector_db: NotRequired[str]          # Vector database
    embedding_model: NotRequired[str]  # Embedding model
    embedding_dimensions: NotRequired[int]
    chunk_size: NotRequired[int]        # Chunk size for retrieval
    chunk_overlap: NotRequired[int]       # Chunk overlap
    top_k: NotRequired[int]           # Number of results to return
    
    ## Runtime State
    user_data: NotRequired[dict]        # User data being used
    data_volume: NotRequired[str]         # Volume: small, medium, large
    data_freshness: NotRequired[str]     # Freshness: realtime, recent, stale
    
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FAMILY 7: CONTEXT AND MEMORY
    # What state is carried into the current decision
    # ═══════════════════════════════════════════════════════════════════════════
    
    ## Config
    conversation_history_length: NotRequired[int]  # Configured history length
    max_context_tokens: NotRequired[int]    # Configured max tokens
    
    ## Runtime State (observed/derived context)
    context_window_usage: NotRequired[dict]  # Current usage
    multi_agent_context: NotRequired[dict]   # Multi-agent context
    session_state: NotRequired[dict]         # Current session state
    persistent_memory: NotRequired[dict]    # Persistent memory
    project_memory: NotRequired[dict]        # Project memory
    feedback_memory: NotRequired[dict]         # Feedback memory
    system_instructions: NotRequired[list[str]]  # Active system instructions
    
    ## Missing Fields (added)
    context_snapshot_id: NotRequired[str]
    context_freshness: NotRequired[str]       # fresh, stale
    context_clarity: NotRequired[str]         # clear, ambiguous, unclear (context-specific)
    context_change_detected: NotRequired[bool]
    context_conflict_state: NotRequired[str]
    context_revalidation_required: NotRequired[bool]
    
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FAMILY 8: SAFETY, SECURITY, COMPLIANCE, AND BOUNDARIES
    # What the system is not allowed to violate
    # ═══════════════════════════════════════════════════════════════════════════
    
    ## Config
    content_filters: NotRequired[list[str]]  # Active content filters
    secret_handling: NotRequired[str]     # How secrets are handled
    pii_sensitivity: NotRequired[str]   # PII sensitivity level
    audit_requirements: NotRequired[dict]  # Audit requirements
    
    ## Runtime State
    sandbox_mode: NotRequired[str]        # Current sandbox mode
    
    ## Missing Fields (added)
    policy_scope: NotRequired[list[str]]
    data_classification: NotRequired[str]  # public, internal, confidential, restricted
    tenant_scope: NotRequired[str]
    cross_tenant_allowed: NotRequired[bool]  # Default: false
    human_review_required: NotRequired[bool]
    policy_evaluation_ref: NotRequired[str]
    
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FAMILY 9: OUTPUT CONTRACT
    # What kind of result is expected
    # ═══════════════════════════════════════════════════════════════════════════
    
    ## Config
    format: NotRequired[str]              # Expected format: json, text, markdown
    verbosity: NotRequired[str]          # terse, normal, detailed
    audience: NotRequired[str]         # Target audience
    determinism_required: NotRequired[bool]
    
    ## Missing Fields (added)
    explainability_required: NotRequired[bool]
    reversibility_requirement: NotRequired[bool]
    citation_requirement: NotRequired[bool]
    decision_lineage_ref: NotRequired[str]
    source_provenance_ref: NotRequired[str]
    
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FAMILY 10: EVALUATION, TELEMETRY, AND OUTCOMES
    # How success is measured
    # ═══════════════════════════════════════════════════════════════════════════
    
    ## Config
    grader: NotRequired[str]           # Grader to use
    rubric: NotRequired[dict]            # Evaluation rubric
    baseline: NotRequired[dict]         # Baseline metrics
    
    ## Outcome State (measured after execution)
    eval_score: NotRequired[float]       # Evaluation score
    duration_seconds: NotRequired[float] # Execution duration
    cost_llm: NotRequired[float]        # LLM cost
    cost_infra: NotRequired[float]       # Infrastructure cost
    steps_taken: NotRequired[int]      # Number of steps executed
    user_confirmations: NotRequired[int]  # Number of confirmations
    errors_encountered: NotRequired[list[str]]  # Errors encountered
    completeness: NotRequired[str]        # complete, partial, failed
    failure_rate: NotRequired[float]     # Failure rate
    
    ## Missing Fields (added)
    ttft_ms: NotRequired[int]         # Time to first token (ms)
    tokens_per_second: NotRequired[float]  # Generation speed
    
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EXECUTION TRACKING FIELDS (from original v2)
    # These are preserved and mapped to appropriate families
    # ═══════════════════════════════════════════════════════════════════════════
    
    execution_request_id: str           # Family 1: Identity
    policy_resolution: dict | None       # Family 8: Safety
    approval_status: str | None         # Family 1: Authority
    backend_selected: str | None        # Family 4: Routing (renamed from routing_strategy)
    result: dict | None               # Family 10: Outcomes
    history: list[dict]                # Family 7: Context
    
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MULTI-TENANT FIELDS (added for platform)
    # ═══════════════════════════════════════════════════════════════════════════
    
    tenant_id: str                     # Family 1: Identity
    tenant_partition_key: NotRequired[str]
    namespace_key: NotRequired[str]
    basis_ref: NotRequired[str]       # Reference to basis for decision
    success_metric: NotRequired[str]  # Metric for measuring success
```

### Duplicate Removal Summary

The following duplicates were identified and consolidated:

| Field | Original Locations | Canonical Location |
|-------|-----------------|-------------------|
| `skill_version` | Core, Skill Configuration, Versioning | Family 5: Skill, Prompt, Tooling Layer |
| `mcp_servers` | Core, Skill Configuration | Family 5: Skill, Prompt, Tooling Layer |
| `fallback_chain` | Agent Architecture, Task-Model Routing | Family 4: Routing, Planning, Orchestration |

### Field Category Summary

| Category | Families | Count |
|----------|----------|-------|
| Config (set ahead of time) | 1, 2, 3, 4, 5, 6, 9 | ~35 fields |
| Runtime State (during execution) | 1, 2, 3, 5, 6, 7, 8 | ~30 fields |
| Decision State (chosen) | 1, 4 | ~10 fields |
| Outcome State (after execution) | 3, 10 | ~20 fields |

### Implementation Note

This schema can be split into separate TypedDict classes:

- `ExecutionConfig` - Config fields only
- `RuntimeState` - Runtime state fields only  
- `ContextState` - Context/memory fields
- `RoutingDecision` - Decision state fields
- `GovernanceState` - Safety/security fields
- `OutputContract` - Output expectation fields
- `EvaluationResult` - Outcome fields

This separation enables clearer validation and state management.

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