# Schema Expansion Before Orchestrator Completion

This document defines the modular schema expansion plan required to support all verticals before the orchestrator unit is completed.

---

## Overview

The orchestrator (LangGraph-based workflow engine) requires a solid foundation of entities and relationships. Many modules discussed in the architecture must be modeled before the orchestrator can effectively manage complex workflows.

### Purpose

1. **Define dependencies** - What must exist before the orchestrator
2. **Modular planning** - Each module can be implemented independently
3. **Growth stages** - Startup → Growth → Enterprise applicability
4. **Dependency order** - Which modules enable others

---

## Module Dependency Map

```
┌─────────────────────────────────────────────────────────────────┐
│                    MANDATORY BEFORE ORCHESTRATOR                │
├─────────────────────────────────────────────────────────────────┤
│  1. Runtime Registry & Selection                                │
│  2. Channel / Branch / Worker                                  │
│  4. Tool Registry                                                │
│  6. Context Window / Compaction                                │
├─────────────────────────────────────────────────────────────────┤
│                      PHASE 2 (Post-Orchestrator v1)              │
├─────────────────────────────────────────────────────────────────┤
│  3. Skill Lifecycle                                             │
│  5. Agent Capability Mgmt                                       │
│  7. Managed Runtime Governance                                  │
│  8. Policy Governance                                          │
│  9. Guardrails / Privacy                                        │
│ 10. Audit & Evidence                                           │
├─────────────────────────────────────────────────────────────────┤
│                      PHASE 3 (Enterprise)                       │
├─────────────────────────────────────────────────────────────────┤
│ 11. Fine-Grained Access Control                                 │
│ 12. Access Reviews                                              │
│ 13. Identity Governance                                         │
│ 14. Data Governance                                             │
│ 15. Policy Packs & Compliance Packs                             │
│ 16. SLA Governance                                              │
│ 17-24. Process & Business Modules                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## A. Runtime + AI Asset Modules

### 1. Runtime Registry & Selection

**Purpose**: Track available runtimes (LangGraph, OpenAI Agents, Claude Agent, etc.) and their capabilities.

**Why Required Before Orchestrator**: The orchestrator must know which runtime to dispatch tasks to.

| Entity | Description |
|--------|-------------|
| `runtime` | Runtime definition (type, capabilities) |
| `runtime_capability` | Capabilities per runtime |
| `runtime_selection_policy` | Tenant-specific runtime selection rules |
| `runtime_fallback_order` | Fallback chain per tenant |

**Links to Existing**:
- `employee.agent_runtime_preference` → runtime.id

**Growth Stage**: Startup (core)

**Dependencies**: None

---

### 2. Channel / Branch / Worker / Cortex

**Purpose**: Thread/branch management for multi-turn conversations and session state.

**Why Required Before Orchestrator**: Orchestrator manages workflows that span multiple channels and branches.

| Entity | Description |
|--------|-------------|
| `channel` | Communication channel (web, slack, discord) |
| `branch` | Conversation branch/fork |
| `worker` | Worker thread execution |
| `cortex_context` | Compaction/briefing context |

**Links to Existing**:
- `thread.channel_id` → channel.id
- `execution_request.branch_id` → branch.id

**Growth Stage**: Startup (core)

**Dependencies**: 1. Runtime Registry

---

### 3. Skill Lifecycle & Evaluation

**Purpose**: Track agent skills, versions, evaluation metrics, and performance.

**Why Required Before Orchestrator**: Optional for v1 - skills enhance orchestration but aren't required.

| Entity | Description |
|--------|-------------|
| `skill` | Skill definition |
| `skill_version` | Version history |
| `skill_evaluation` | Quality/performance evaluation |
| `skill_training_data` | Training corpus (future) |

**Links to Existing**:
- `employee.skill_ids` → skill.id

**Growth Stage**: Growth (v2)

**Dependencies**: 1, 2, 5

---

### 4. Tool Registry & Governance

**Purpose**: Central registry of available tools, governance, and approval workflows.

**Why Required Before Orchestrator**: Orchestrator dispatches tasks that may require tool execution.

| Entity | Description |
|--------|-------------|
| `tool` | Tool definition |
| `tool_version` | Version history |
| `tool_category` | Category grouping |
| `tool_approval` | Approval for tool usage |
| `tool_governance_policy` | Usage policies |

**Links to Existing**:
- `execution_request.tool_ids` → tool.id

**Growth Stage**: Startup (core)

**Dependencies**: 1

---

### 5. Agent Capability Management

**Purpose**: Track agent capabilities, entitlements, and quota allocations.

**Why Required Before Orchestrator**: Orchestrator must verify agent has permission/capability before execution.

| Entity | Description |
|--------|-------------|
| `agent_capability` | Capability definition |
| `agent_entitlement` | Per-tenant entitlement |
| `agent_quota` | Usage quotas |
| `agent_usage_record` | Actual usage tracking |

**Links to Existing**:
- `tenant.agent_entitlements` → agent_entitlement.id

**Growth Stage**: Growth

**Dependencies**: 1

---

### 6. Managed Runtime Governance

**Purpose**: Runtime health, monitoring, and governance policies.

**Why Required Before Orchestrator**: Required for reliable execution dispatch.

| Entity | Description |
|--------|-------------|
| `runtime_instance` | Running runtime instance |
| `runtime_health` | Health status |
| `runtime_metrics` | Performance metrics |
| `runtime_policy` | Governance policies |

**Links to Existing**:
- `runtime.instance_id` → runtime_instance.id

**Growth Stage**: Startup (core)

**Dependencies**: 1

---

### 7. Context Window / Compaction Governance

**Purpose**: Manage context budgets, compaction triggers, and token accounting.

**Why Required Before Orchestrator**: Ensures orchestrator doesn't exceed context limits.

| Entity | Description |
|--------|-------------|
| `context_budget` | Budget per task type |
| `compaction_policy` | Compaction triggers |
| `compaction_summary` | Briefings/summaries |
| `token_accounting` | Token usage tracking |

**Links to Existing**:
- `execution_request.compaction_summary_id` → compaction_summary.id

**Growth Stage**: Startup (core)

**Dependencies**: 1, 2

---

## B. Governance + Control Modules

### 8. Policy Governance

**Purpose**: Central policy management, versioning, and audit.

**Why Required Before Orchestrator**: Required for policy-based routing and execution controls.

| Entity | Description |
|--------|-------------|
| `policy` | Policy definition |
| `policy_version` | Version history |
| `policy_attachment` | Policy → tenant/user mapping |
| `policy_violation` | Violation tracking |

**Links to Existing**:
- `tenant.policy_ids` → policy.id
- `execution_request.policy_id` → policy.id

**Growth Stage**: Startup (core)

**Dependencies**: 1, 4

---

### 9. Guardrails / Privacy / Compliance

**Purpose**: Runtime guardrails, PII handling, and compliance controls.

**Why Required Before Orchestrator**: Required for safe execution.

| Entity | Description |
|--------|-------------|
| `guardrail` | Guardrail definition |
| `guardrail_config` | Per-tenant configuration |
| `pii_rule` | PII detection rules |
| `compliance_control` | Compliance requirements |

**Growth Stage**: Startup (core)

**Dependencies**: 8

---

### 10. Audit & Evidence

**Purpose**: Immutable audit logs and evidence preservation.

**Why Required Before Orchestrator**: Required for compliance and debugging.

| Entity | Description |
|--------|-------------|
| `audit_log` | Immutable audit entry |
| `evidence_record` | Evidence preservation |
| `audit_trail` | Trail linking |

**Growth Stage**: Startup (core)

**Dependencies**: 8, 9

---

### 11. Fine-Grained Access Control

**Purpose**: RBAC, ABAC, and resource-level permissions.

**Why Required Before Orchestrator**: Enterprise requirement - can defer to v2.

| Entity | Description |
|--------|-------------|
| `permission` | Permission definition |
| `role` | Role definition |
| `role_permission` | Role → permission mapping |
| `user_role` | User → role mapping |
| `resource_policy` | Resource-level policies |

**Growth Stage**: Enterprise

**Dependencies**: 10

---

### 12. Access Reviews

**Purpose**: Periodic access certification and review workflows.

**Why Required Before Orchestrator**: Enterprise requirement.

| Entity | Description |
|--------|-------------|
| `access_review` | Review campaign |
| `access_review_item` | Items under review |
| `access_review_result` | Review decisions |

**Growth Stage**: Enterprise

**Dependencies**: 11

---

### 13. Identity Governance

**Purpose**: Identity lifecycle, SSO, and provisioning.

**Why Required Before Orchestrator**: Enterprise requirement.

| Entity | Description |
|--------|-------------|
| `identity` | Identity record |
| `identity_provider` | IdP configuration |
| `provisioning_rule` | Auto-provisioning rules |

**Growth Stage**: Enterprise

**Dependencies**: 11, 12

---

### 14. Data Governance

**Purpose**: Data classification, lineage, and retention.

**Why Required Before Orchestrator**: Enterprise requirement.

| Entity | Description |
|--------|-------------|
| `data_classification` | Classification schema |
| `data_lineage` | Data flow tracking |
| `retention_policy` | Retention rules |

**Growth Stage**: Enterprise

**Dependencies**: 9, 10

---

## C. Process + Business Modules

### 15. Policy Packs & Compliance Packs

**Purpose**: Bundled policies for common compliance frameworks (SOC2, HIPAA, etc.).

**Why Required Before Orchestrator**: Post-orchestrator v1.

| Entity | Description |
|--------|-------------|
| `policy_pack` | Policy bundle |
| `compliance_pack` | Compliance bundle |
| `pack_mapping` | Pack → policies mapping |

**Growth Stage**: Enterprise

**Dependencies**: 8

---

### 16. SLA Governance & Breach Management

**Purpose**: SLA tracking, breach detection, and remediation.

**Why Required Before Orchestrator**: Post-orchestrator v1.

| Entity | Description |
|--------|-------------|
| `sla` | SLA definition |
| `sla_breach` | Breach record |
| `sla_remediation` | Remediation tracking |

**Growth Stage**: Growth

**Dependencies**: 8, 10

---

### 17. Employee Onboarding Flow

**Purpose**: Onboarding workflow automation.

**Why Required Before Orchestrator**: Post-orchestrator v1.

**Dependencies**: 16+

---

### 18. Master Data Upload Flow

**Purpose**: Bulk data import and validation.

**Why Required Before Orchestrator**: Post-orchestrator v1.

**Dependencies**: 14

---

### 19. Event Calendar & Time Governance

**Purpose**: Event scheduling and time-based governance.

**Why Required Before Orchestrator**: Post-orchestrator v1.

**Dependencies**: 16+

---

### 20. Feedback / Suggestions / Issues / Bugs

**Purpose**: Feedback collection and issue tracking.

**Why Required Before Orchestrator**: Post-orchestrator v1.

**Dependencies**: 10

---

### 21-24. Business Modules

Customer expectations, competitor benchmarking, industry compliance, government compliance - these are enterprise extensions.

**Dependencies**: All above

---

## Recommended Schema Expansion Sequence

### Phase 0: Pre-Orchestrator (Mandatory)

These modules MUST be modeled before orchestrator completion:

1. **Runtime Registry & Selection** (1)
2. **Channel / Branch / Worker / Cortex** (2)
3. **Tool Registry & Governance** (4)
4. **Managed Runtime Governance** (6)
5. **Context Window / Compaction** (7)

### Phase 1: Orchestrator v1 Enablement

These support the core orchestrator:

6. **Policy Governance** (8)
7. **Guardrails / Privacy** (9)
8. **Audit & Evidence** (10)

### Phase 2: Growth Features

9. **Skill Lifecycle** (3)
10. **Agent Capability Management** (5)
11. **SLA Governance** (16)

### Phase 3: Enterprise

Everything else (11-24)

---

## Summary: Mandatory Before Orchestrator Completion

| Module | Priority | Reason |
|--------|----------|--------|
| Runtime Registry & Selection | P0 | Orchestrator dispatches to runtimes |
| Channel / Branch / Worker | P0 | Orchestrator manages multi-turn |
| Tool Registry | P0 | Orchestrator executes tools |
| Managed Runtime Governance | P0 | Orchestrator needs healthy runtimes |
| Context Window / Compaction | P0 | Orchestrator must stay within limits |

**Minimum viable schema before orchestrator**: Modules 1, 2, 4, 6, 7

---

## Next Steps

1. Create `docs/data-model/schema-expansion-roadmap.md` with detailed entity specs
2. Create `docs/architecture/module-roadmap-v2.md` with implementation order
3. Begin implementation of Phase 0 modules

---

_End of Schema Expansion Plan_