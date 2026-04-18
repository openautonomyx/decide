# Design Summary v1

This document summarizes the core design decisions for the Autonomyx platform.

---

## Core Entity Split: Employee vs Agent

### Separation
- **Employee** = Human entity (real-world person)
- **Agent** = AI entity (automated agent)

### Key Rule
> Employee and Agent are **never merged**. They have separate IDs and tables.

### Relationships
- One employee can own multiple agents
- One employee can supervise another employee's agent
- Agent projects a "title" but doesn't hold real HR data

---

## Collaboration Containers

### Three Distinct Entities

| Entity | Purpose | Timeline | Channel |
|--------|---------|----------|---------|
| **Product** | Business function | Persistent | Required |
| **Project** | Execution | Short-term | Optional |
| **Group** | Community/interest | Variable | Required |

### Not Merged
Product ≠ Project ≠ Group. Each is first-class with different lifecycle.

---

## Workflow Model

### First-Class Entities
- Task (atomic unit)
- Task dependency (explicit relationships)
- Task assignment history (audit trail)
- Deadline (separate from task end)
- Milestone (progress checkpoints)
- Reminder (notification triggers)
- Escalation (risk notification)

### Why Separate?
Each serves different purpose in work management. Not properties of task.

---

## Control Plane

### Critical Distinctions

| Distinction | Entities |
|------------|----------|
| Human approval vs Rule decision | approval_request vs decision_record |
| Default vs Override vs Effective | policy_resolution vs override_record |
| Delegation vs Acting vs Transfer | responsibility_assignment |
| Backend selection vs Fallback vs Used | backend_selection vs fallback_event vs usage_record |

### Execution Trace
Every request maintains full trace:
1. execution_request created
2. policy_resolution (rule decision)
3. override_record (if human overrides)
4. approval_request (if human approval)
5. backend_selection (routing)
6. fallback_event (if needed)
7. execution_history (audit)
8. usage_record (cost tracking)
9. memory_checkpoint (state)

---

## Schema Overview (73 Tables)

### By Domain
- Master data: 12 tables
- Employee: 7 tables
- Agent: 9 tables
- Prompt/Skills/Goals: 14 tables
- Product/Project/Group: 4 tables
- Workflow: 16 tables
- Channels: 5 tables
- Decision/Control: 12 tables
- Tenant Policy: 3 tables

### Key Design Principles
1. All IDs use VARCHAR(36) UUIDs
2. Audit fields on all tables (created_at, updated_at)
3. Foreign keys to earlier migrations
4. No DROP statements in migrations

---

## State Machines

### Entities with Lifecycles
- task: pending → assigned → in_progress → completed
- approval_request: pending → approved/denied
- execution_request: pending → routed → running → success/error
- escalation: open → acknowledged → in_progress → resolved

---

## Governance

### Profiles (External References)
- prompt_profile_master → prompt templates
- guardrail_profile_master → safety rules
- approval_profile_master → approval rules
- channel_profile_master → channel settings

### Agent Governance
Links to profiles via agent_governance_profile

---

## Open Questions

1. **Agent credentials** - Need dedicated table for agent assessments?
2. **Nested comments** - Should task_comment support nesting?
3. **Custom fields** - Need JSONB extension on task?

---

## Dependencies

| Migration | Tables | Dependencies |
|-----------|--------|-------------|
| 001 | Master data | None |
| 002 | Tenant/Employee | 001 |
| 003 | Agent layer | 002 |
| 004 | Prompt/Skills/Goals | 001, 002, 003 |
| 005 | Product/Project/Group | 002, 003 |
| 006 | Workflow | 002, 003, 004, 005 |
| 007 | Channels | 002, 003, 004 |
| 008 | Tenant Policy | 002, 007 |

---

## Document Maps

| Document | Location |
|----------|----------|
| Schema | docs/data-model/schema-v1.sql |
| Migrations | db/migrations/ |
| State machines | docs/architecture/state-machines/ |
| Agent profile | docs/architecture/agent-profile-schema.md |
| Employee | docs/architecture/employee-schema.md |
| Collaboration | docs/architecture/collaboration-model.md |
| Workflow | docs/architecture/workflow-model.md |
| Control plane | docs/architecture/control-plane-model.md |
| Naming | docs/data-model/naming-conventions.md |

---

## Runtime Architecture v2 Note

**Status**: Additive major architecture update (do not remove existing model)

A new Runtime Architecture v2 has been added alongside this design summary:

- **Document**: `docs/architecture/runtime-architecture-v2.md`
- **Key changes**:
  - LangGraph as top-level orchestrator (additive)
  - Multiple worker runtimes with registry (additive)
  - Cortex memory layer (additive)
  - Runtime selection policy (additive)
- **What remains unchanged**: All 73 tables, all control-plane entities, all entity splits (Employee/Agent, Product/Project/Group), all workflow model, RBAC, audit
- **v1 model**: Remains fully functional as baseline
- **Migration**: Phased rollout, no removal

See `runtime-architecture-v2.md` for full specification.

---

## Memory & Storage Decision Note

**Status**: Additive storage layer decision (do not redesign schemas)

A storage decision matrix has been added:

- **Document**: `docs/architecture/memory-storage-decision.md`
- **Key recommendations**:
  - Redis for hot working memory/cache/session state
  - SingleStore for primary long-term vector + hybrid retrieval
  - Postgres for operational/control-plane truth (unchanged)
  - Postgres for checkpoints and audit (unchanged)
- **What remains unchanged**: All control-plane entities, operational truth in Postgres
- **Phase 1**: Working memory (Redis) + semantic vector (SingleStore)
- **Phase 2**: Cortex checkpoints + briefing

See `memory-storage-decision.md` for full specification.

---

## Runtime Selection Implementation Note

**Status**: Code implementation for runtime architecture v2

Implementation modules added:

- **app/core/runtime_registry.py** - Runtime registry with 5 runtimes
- **docs/architecture/runtime-selection-implementation.md** - Integration guide
- **Key features**:
  - Task-type detection (coding, conversation, autonomous, collaboration, simple)
  - Runtime selection by task_type and tenant policy
  - Backend mapping (runtime knows which provider/model to use)
  - Fallback chain (runtime fallback → backend fallback)
  - Full audit trail in execution_history
- **What remains unchanged**: backend_selection table, usage_record, execution_history

See `runtime-selection-implementation.md` for full API and integration details.

---

## Memory & Storage Implementation Note

**Status**: Implementation for memory layers

Implementation modules:

- **app/memory/types.py** - Memory types + Cortex categories (12 types)
- **app/memory/working_memory.py** - Redis working memory
- **app/memory/episodic_memory.py** - Redis cache + Postgres
- **app/memory/semantic_memory.py** - SingleStore adapter
- **app/memory/checkpoints.py** - Postgres adapter
- **app/memory/cortex.py** - Redis + Postgres briefings
- **app/memory/compaction.py** - Context budget + compaction
- **docs/architecture/runtime-memory-implementation.md** - Integration guide
- **docs/architecture/cortex-implementation.md** - Cortex details

Key features:
- Typed memory categories (fact, preference, decision, etc.)
- Context budget enforcement (80% threshold)
- Compaction summaries before context fills
- Checkpoint hooks at configurable intervals

See `cortex-implementation.md` for full details.

---

## OpenAI Channel Runtime Implementation

**Status**: Implementation of human-facing runtime

Implementation modules:

- **app/runtime/types.py** - Runtime types + ChannelRuntimeType
- **app/runtime/channel_runtime.py** - Abstract channel interface
- **app/runtime/openai_channel_runtime.py** - OpenAI Agents SDK adapter
- **docs/architecture/openai-channel-runtime.md** - Integration guide

Key features:
- Channel abstraction for human-facing conversation
- OpenAI Agents SDK integration (adapter mode ready)
- Session context with message history
- Tool handoff support
- Integrates with runtime selection

What is implemented:
- Abstract ChannelRuntime base class
- OpenAIChannelRuntime adapter
- Session management interface

What is placeholder:
- Actual SDK integration (waiting for package)
- Session persistence (would use Redis)
- Tool registry

See `openai-channel-runtime.md` for full details.

---

## Phase 0 API Implementation

**Status**: FastAPI layer for pre-orchestrator services

Implementation files:

- **app/api/runtime.py** - Runtime registry endpoints (8 endpoints)
- **app/api/channel.py** - Channel/Branch/Worker/Cortex endpoints (15 endpoints)
- **app/api/tool.py** - Tool registry endpoints (13 endpoints)
- **app/api/skill.py** - Skill lifecycle endpoints (10 endpoints)
- **app/api/context.py** - Context/Token/Compaction endpoints (13 endpoints)
- **app/main.py** - Router registration updated
- **docs/architecture/phase-0-api-implementation.md** - Endpoint documentation

Key features:
- Admin CRUD endpoints for all Phase 0 services
- Runtime/internal APIs for orchestrator communication
- Clean request/response schemas
- Consistent endpoint patterns

See `phase-0-api-implementation.md` for full endpoint documentation.

---

## Orchestrator Core Implementation

**Status**: Phase 1 orchestrator complete

Implementation files:

- **app/orchestrator/types.py** - TaskType, OrchestratorStatus, ExecutionState, etc.
- **app/orchestrator/state.py** - ExecutionStateStore for state management
- **app/orchestrator/router.py** - Task detection + runtime selection
- **app/orchestrator/engine.py** - 10-stage execution pipeline
- **tests/test_orchestrator.py** - Minimal test coverage
- **docs/architecture/orchestrator-core-implementation.md** - Full documentation

Key features:
- 10-stage execution pipeline (intake → result)
- Reuses all Phase 0 services
- Task type detection (keyword-based)
- Runtime selection via RuntimeRegistryService
- Channel/Branch/Worker context setup
- Budget check via ContextBudgetService
- Tool/Skill resolution via respective services

What is real:
- Execution state management
- Task type detection
- Runtime selection
- Context creation
- Budget checking

What is stubbed:
- Actual runtime invocation
- Policy evaluation
- Guardrails
- Compaction execution
- HITL approval

See `orchestrator-core-implementation.md` for full details.

---

## Orchestrator Phase 2: Policy & Guardrails

**Status**: Policy and guardrail integration complete

Implementation files:

- **app/orchestrator/policy_gate.py** - Policy evaluation (allow/deny/approve/escalate)
- **app/orchestrator/guardrails.py** - Input/output safety checks
- **app/orchestrator/approval_gate.py** - HITL approval workflow
- **tests/test_orchestrator_phase2.py** - Phase 2 test coverage
- **docs/architecture/orchestrator-phase-2-policy-guardrails.md** - Full documentation

Key features:
- Policy gate with rule-based evaluation
- Default rules: block destructive commands, require approval for high-risk tools
- Guardrails: PII detection (SSN, credit card), tool blocking, skill flagging
- Approval workflow: create, approve, reject, check status, expiration
- Extension hooks for OPA integration

What is real:
- Policy decisions (allow/deny/require_approval/escalate)
- Guardrail evaluation (input, tools, skills)
- Approval workflow

What is stubbed:
- OPA integration
- Custom guardrail registry
- Output guardrails

See `orchestrator-phase-2-policy-guardrails.md` for full details.

_End of Design Summary_