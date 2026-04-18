# Pre-Orchestrator API Implementation Plan

This document defines the API implementation boundaries for each mandatory module required before orchestrator completion.

---

## Overview

### Guiding Principles

1. **Internal-first**: Many modules are internal and don't need external APIs
2. **Admin APIs**: Management operations for admins only
3. **Runtime APIs**: Lightweight interfaces for the orchestrator
4. **Doc-only**: Features that can wait until later phases

### Module Categories

| Category | Description | Examples |
|----------|-------------|----------|
| Internal | Used by orchestrator only | Runtime selection, context budget |
| Admin | Management interfaces | Tool registry, policy management |
| Runtime | Orchestrator-facing | Tool dispatch, checkpointing |
| External | User-facing | Channel chat, feedback |

---

## Module Implementation Plans

### 1. Runtime Registry & Selection

**Status**: EXISTING (extends for orchestrator)

**Purpose**: Track available runtimes and select best runtime for task execution

**Service Boundaries**:
- `RuntimeRegistryService`: Central registry management
- `RuntimeSelector`: Task-type to runtime mapping

**API Boundaries**:

| API | Type | Who Uses It | Status |
|-----|------|-------------|--------|
| `GET /runtimes` | Admin | Platform admin | IMPLEMENT |
| `GET /runtimes/{id}` | Admin | Platform admin | IMPLEMENT |
| `POST /runtimes` | Admin | Platform admin | IMPLEMENT |
| `PATCH /runtimes/{id}` | Admin | Platform admin | IMPLEMENT |
| `GET /runtimes/select` | Runtime | Orchestrator | IMPLEMENT |
| `GET /health` | Runtime | Orchestrator | IMPLEMENT |

**Internal-only**:
- Runtime selection logic
- Fallback chain resolution
- Health check aggregation

**Doc-only until Phase 2**:
- Runtime metrics dashboard
- Cost estimation APIs

---

### 2. Channel / Branch / Worker / Cortex

**Status**: EXISTING (memory layer exists)

**Purpose**: Thread management, branch forking, worker execution context

**Service Boundaries**:
- `ChannelService`: Channel lifecycle
- `BranchService`: Branch forking/merging
- `WorkerService`: Execution context
- `CortexService`: Context compaction/briefing

**API Boundaries**:

| API | Type | Who Uses It | Status |
|-----|------|-------------|--------|
| `GET /channels` | Admin | Platform admin | IMPLEMENT |
| `POST /channels` | Admin | Platform admin | IMPLEMENT |
| `GET /threads/{id}/branches` | Runtime | Orchestrator | IMPLEMENT |
| `POST /threads/{id}/branch` | Runtime | Orchestrator | IMPLEMENT |
| `GET /workers/{id}` | Runtime | Orchestrator | IMPLEMENT |
| `POST /workers` | Runtime | Orchestrator | IMPLEMENT |
| `PATCH /workers/{id}/state` | Runtime | Orchestrator | IMPLEMENT |
| `GET /cortex/{thread_id}/summary` | Runtime | Orchestrator | IMPLEMENT |

**Internal-only**:
- Branch merge logic
- Worker state management
- Cortex compaction triggers

**Doc-only until Phase 2**:
- Channel webhook configs
- Branch visualization

---

### 3. Tool Registry & Governance

**Status**: NEW (from claude-coder)

**Purpose**: Central tool registry with approval workflows

**Service Boundaries**:
- `ToolRegistry`: Tool registration and discovery
- `ToolGovernance`: Approval and usage policies

**API Boundaries**:

| API | Type | Who Uses It | Status |
|-----|------|-------------|--------|
| `GET /tools` | Admin | Platform admin | IMPLEMENT |
| `GET /tools/{id}` | Runtime | Orchestrator | IMPLEMENT |
| `POST /tools` | Admin | Platform admin | IMPLEMENT |
| `PATCH /tools/{id}` | Admin | Platform admin | IMPLEMENT |
| `DELETE /tools/{id}` | Admin | Platform admin | IMPLEMENT |
| `POST /tools/{id}/approve` | Admin | Compliance admin | IMPLEMENT |
| `GET /tools/categories` | Runtime | Orchestrator | IMPLEMENT |
| `GET /tools/search` | Runtime | Orchestrator | IMPLEMENT |

**Internal-only**:
- Tool execution handlers (not APIs - internal functions)
- Governance policy evaluation

**Doc-only until Phase 2**:
- Tool marketplace
- Tool usage analytics

---

### 4. Skill Lifecycle & Evaluation

**Status**: NEW

**Purpose**: Agent skill management and performance evaluation

**Service Boundaries**:
- `SkillRegistry`: Skill registration and versioning
- `SkillEvaluator`: Performance metrics collection

**API Boundaries**:

| API | Type | Who Uses It | Status |
|-----|------|-------------|--------|
| `GET /skills` | Admin | Platform admin | IMPLEMENT |
| `GET /skills/{id}` | Runtime | Orchestrator | IMPLEMENT |
| `POST /skills` | Admin | Platform admin | IMPLEMENT |
| `PATCH /skills/{id}` | Admin | Platform admin | IMPLEMENT |
| `DELETE /skills/{id}` | Admin | Platform admin | IMPLEMENT |
| `GET /skills/{id}/versions` | Admin | Platform admin | IMPLEMENT |
| `GET /skills/{id}/evaluations` | Admin | Platform admin | IMPLEMENT |
| `POST /skills/{id}/evaluate` | Internal | System (scheduled) | IMPLEMENT |

**Internal-only**:
- Skill evaluation scheduler
- Training data management

**Doc-only until Phase 2** (or later):
- Skill marketplace
- Skill recommendation engine

---

### 5. Policy Governance

**Status**: PARTIAL (existing in claude-coder)

**Purpose**: Central policy management, versioning, attachment

**Service Boundaries**:
- `PolicyService`: Policy CRUD and versioning
- `PolicyResolver`: Request-time policy resolution

**API Boundaries**:

| API | Type | Who Uses It | Status |
|-----|------|-------------|--------|
| `GET /policies` | Admin | Platform admin | IMPLEMENT |
| `GET /policies/{id}` | Runtime | Orchestrator | IMPLEMENT |
| `POST /policies` | Admin | Platform admin | IMPLEMENT |
| `PATCH /policies/{id}` | Admin | Platform admin | IMPLEMENT |
| `DELETE /policies/{id}` | Admin | Platform admin | IMPLEMENT |
| `GET /policies/{id}/versions` | Admin | Platform admin | IMPLEMENT |
| `POST /policies/{id}/attach` | Admin | Tenant admin | IMPLEMENT |
| `GET /policies/resolve` | Runtime | Orchestrator | IMPLEMENT |
| `GET /policies/violations` | Admin | Platform admin | IMPLEMENT |

**Internal-only**:
- Policy evaluation engine
- Violation detection

**Doc-only until Phase 2**:
- Policy templates
- Policy impact analysis

---

### 6. Guardrails / Privacy / Compliance

**Status**: NEW

**Purpose**: Runtime guardrails, PII handling, compliance controls

**Service Boundaries**:
- `GuardrailService`: Guardrail enforcement
- `PIIRulesService`: PII detection and handling
- `ComplianceService`: Compliance control checks

**API Boundaries**:

| API | Type | Who Uses It | Status |
|-----|------|-------------|--------|
| `GET /guardrails` | Admin | Platform admin | IMPLEMENT |
| `POST /guardrails` | Admin | Platform admin | IMPLEMENT |
| `PATCH /guardrails/{id}` | Admin | Platform admin | IMPLEMENT |
| `GET /guardrails/check` | Runtime | Orchestrator | IMPLEMENT |
| `GET /pii/rules` | Admin | Compliance admin | IMPLEMENT |
| `POST /pii/rules` | Admin | Compliance admin | IMPLEMENT |
| `GET /compliance/checks` | Admin | Compliance admin | IMPLEMENT |
| `POST /compliance/run` | Admin | Compliance admin | IMPLEMENT |

**Internal-only**:
- Guardrail evaluation (called by orchestrator)
- PII pattern matching
- Compliance rule engine

**Doc-only until Phase 2**:
- Compliance reports
- Audit trails visualization

---

### 7. Fine-Grained Access Control

**Status**: NEW (can defer to Phase 2)

**Purpose**: RBAC, ABAC, resource-level permissions

**Service Boundaries**:
- `AccessControlService`: Permission evaluation
- `RoleService`: Role management
- `PermissionService`: Permission definitions

**API Boundaries**:

| API | Type | Who Uses It | Status |
|-----|------|-------------|--------|
| `GET /permissions` | Admin | Platform admin | DOC-ONLY |
| `POST /permissions` | Admin | Platform admin | DOC-ONLY |
| `GET /roles` | Admin | Tenant admin | DOC-ONLY |
| `POST /roles` | Admin | Tenant admin | DOC-ONLY |
| `PATCH /roles/{id}` | Admin | Tenant admin | DOC-ONLY |
| `DELETE /roles/{id}` | Admin | Tenant admin | DOC-ONLY |
| `GET /roles/{id}/permissions` | Admin | Tenant admin | DOC-ONLY |
| `POST /users/{id}/roles` | Admin | Tenant admin | DOC-ONLY |
| `GET /access/check` | Runtime | Orchestrator | DOC-ONLY |

**Status**: DEFER to Phase 2 (enterprise feature)

---

### 8. Audit & Evidence

**Status**: PARTIAL (existing audit.py)

**Purpose**: Immutable audit logs and evidence preservation

**Service Boundaries**:
- `AuditService`: Audit log creation and retrieval
- `EvidenceService`: Evidence preservation

**API Boundaries**:

| API | Type | Who Uses It | Status |
|-----|------|-------------|--------|
| `GET /audit/logs` | Admin | Compliance admin | IMPLEMENT |
| `GET /audit/logs/{id}` | Admin | Compliance admin | IMPLEMENT |
| `POST /audit/logs/search` | Admin | Compliance admin | IMPLEMENT |
| `GET /evidence/{id}` | Admin | Compliance admin | IMPLEMENT |
| `POST /evidence` | Runtime | Orchestrator | IMPLEMENT |
| `GET /audit/trail` | Admin | Compliance admin | IMPLEMENT |

**Internal-only**:
- Audit log write (internal call from services)
- Evidence checksum verification

**Doc-only until Phase 2**:
- Audit dashboard
- Evidence export

---

### 9. Context Window / Compaction Governance

**Status**: EXISTING (compaction.py exists)

**Purpose**: Context budget management and compaction

**Service Boundaries**:
- `ContextBudgetService`: Budget tracking
- `CompactionService`: Summary generation

**API Boundaries**:

| API | Type | Who Uses It | Status |
|-----|------|-------------|--------|
| `GET /context/budgets` | Admin | Platform admin | IMPLEMENT |
| `POST /context/budgets` | Admin | Platform admin | IMPLEMENT |
| `PATCH /context/budgets/{id}` | Admin | Platform admin | IMPLEMENT |
| `GET /context/budgets/{task_type}` | Runtime | Orchestrator | IMPLEMENT |
| `GET /compaction/{thread_id}` | Runtime | Orchestrator | IMPLEMENT |
| `POST /compaction/{thread_id}/trigger` | Runtime | Orchestrator | IMPLEMENT |
| `GET /tokens/usage` | Admin | Platform admin | IMPLEMENT |

**Internal-only**:
- Token estimation
- Compaction triggers
- Summary generation

**Doc-only until Phase 2**:
- Token usage analytics

---

### 10. Event Calendar & Time Governance

**Status**: NEW

**Purpose**: Event scheduling and time-based governance triggers

**Service Boundaries**:
- `EventService`: Event CRUD
- `TimePolicyService`: Time-based rules

**API Boundaries**:

| API | Type | Who Uses It | Status |
|-----|------|-------------|--------|
| `GET /events` | Admin | Platform admin | IMPLEMENT |
| `POST /events` | Admin | Platform admin | IMPLEMENT |
| `PATCH /events/{id}` | Admin | Platform admin | IMPLEMENT |
| `DELETE /events/{id}` | Admin | Platform admin | IMPLEMENT |
| `GET /events/calendar` | External | Users | DOC-ONLY |
| `GET /time-policies` | Admin | Platform admin | IMPLEMENT |
| `POST /time-policies` | Admin | Platform admin | IMPLEMENT |

**Internal-only**:
- Time policy evaluation
- Scheduled job triggers

**Doc-only until Phase 2**:
- Calendar UI
- Event RSVP

---

### 11. SLA Governance & Breach Management

**Status**: NEW

**Purpose**: SLA tracking, breach detection, remediation

**Service Boundaries**:
- `SLAService`: SLA definition and tracking
- `BreachService`: Breach detection and resolution

**API Boundaries**:

| API | Type | Who Uses It | Status |
|-----|------|-------------|--------|
| `GET /slas` | Admin | Platform admin | IMPLEMENT |
| `POST /slas` | Admin | Platform admin | IMPLEMENT |
| `PATCH /slas/{id}` | Admin | Platform admin | IMPLEMENT |
| `DELETE /slas/{id}` | Admin | Platform admin | IMPLEMENT |
| `GET /slas/breaches` | Admin | Platform admin | IMPLEMENT |
| `PATCH /slas/breaches/{id}/acknowledge` | Admin | Platform admin | IMPLEMENT |
| `PATCH /slas/breaches/{id}/resolve` | Admin | Platform admin | IMPLEMENT |
| `GET /slas/check` | Runtime | Orchestrator | IMPLEMENT |

**Internal-only**:
- Breach detection
- SLA metric collection

**Doc-only until Phase 2**:
- SLA dashboards
- Breach analytics

---

## Implementation Priority Matrix

| Module | APIs to Implement | Admin | Runtime | Internal | Doc-Only |
|--------|-------------------|-------|---------|----------|----------|
| 1. Runtime Registry | 6 | 4 | 2 | 3 | 2 |
| 2. Channel/Branch/Worker | 8 | 2 | 6 | 4 | 2 |
| 3. Tool Registry | 8 | 6 | 2 | 2 | 2 |
| 4. Skill Lifecycle | 8 | 6 | 1 | 2 | 2 |
| 5. Policy Governance | 9 | 6 | 2 | 2 | 2 |
| 6. Guardrails | 8 | 4 | 2 | 3 | 2 |
| 7. Access Control | 9 | 6 | 1 | 0 | 9 |
| 8. Audit & Evidence | 6 | 5 | 1 | 2 | 2 |
| 9. Context/Compaction | 7 | 3 | 3 | 3 | 1 |
| 10. Event Calendar | 7 | 5 | 1 | 2 | 2 |
| 11. SLA Governance | 8 | 6 | 1 | 2 | 2 |

---

## Services vs APIs Summary

### Pure Internal Services (No External APIs)

These services are called by the orchestrator internally:

1. **RuntimeSelector** - Selection logic
2. **PolicyResolver** - Policy evaluation
3. **CompactionService** - Context summarization
4. **GuardrailEngine** - Guardrail checks

### Admin-Only Services

These require admin APIs but no runtime APIs:

1. **SkillEvaluator** - Scheduled evaluations
2. **BreachService** - Breach detection
3. **TimePolicyService** - Time-based triggers

### Services Needing Both Admin and Runtime APIs

1. **RuntimeRegistryService** - Health + management
2. **ChannelService** - Branch management + admin
3. **ToolRegistryService** - Tool lookup + admin
4. **PolicyService** - Resolve + admin
5. **AuditService** - Log write (runtime) + admin read

---

## Next Steps

1. Begin Phase 0 API implementation (Modules 1-4, 9)
2. Create service stubs for internal-only services
3. Implement admin APIs for Modules 5-6
4. Defer Module 7 (Access Control) to Phase 2

---

_End of Pre-Orchestrator API Implementation Plan_