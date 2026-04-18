# Module Roadmap v2

This document outlines the implementation roadmap for all modules, organized by dependency order and growth stage.

---

## Roadmap Overview

```
┌────────────────────────────────────────────────────────────────────┐
│                         IMPLEMENTATION PHASES                       │
├──────────────┬──────────────┬──────────────┬──────────────────────┤
│   PHASE 0    │   PHASE 1    │   PHASE 2    │       PHASE 3        │
│   (MUST)     │  (ORCH v1)   │   (GROWTH)   │    (ENTERPRISE)      │
├──────────────┼──────────────┼──────────────┼──────────────────────┤
│  Runtime     │   Policy     │   Skill      │    Access Control    │
│  Registry    │   Governance │   Lifecycle  │    Access Reviews    │
│              │              │              │                      │
│  Channel/    │  Guardrails  │   Agent      │    Identity          │
│  Branch/     │              │   Capability │    Governance        │
│  Worker      │              │              │                      │
│              │  Audit &     │   SLA        │    Data              │
│  Tool        │  Evidence    │   Governance │    Governance         │
│  Registry    │              │              │                      │
│              │              │              │    Policy Packs      │
│  Runtime     │              │              │                      │
│  Governance  │              │              │    Business          │
│              │              │              │    Modules           │
│  Context     │              │              │                      │
│  Compaction  │              │              │                      │
└──────────────┴──────────────┴──────────────┴──────────────────────┘
```

---

## Phase 0: Pre-Orchestrator (Mandatory)

### Module 1: Runtime Registry & Selection

**Status**: EXISTING (needs extension)

**Files**:
- `app/core/runtime_registry.py`
- `app/core/runtime_types.py`
- `app/core/runtime_config.py`
- `app/core/runtime_selection.py`

**Extensions Needed**:
- `runtime_instance` table
- `runtime_health` table
- `runtime_metrics` table

**Implementation**: Extend existing runtime registry with instance tracking

---

### Module 2: Channel / Branch / Worker / Cortex

**Status**: PARTIAL (memory layer exists)

**Files**:
- `app/memory/working_memory.py`
- `app/memory/cortex.py`
- `app/memory/types.py`

**Extensions Needed**:
- `channel` table
- `branch` table
- `worker` table

**Implementation**: Add table definitions for channel/branch/worker

---

### Module 3: Tool Registry & Governance

**Status**: NEW

**Files to Create**:
- `app/governance/tool_registry.py`
- `app/models/tool.py`

**Entities**:
```python
class Tool(Base):
    id = Column(String, primary_key=True)
    name = Column(String)
    category = Column(String)
    description = Column(Text)
    version = Column(String)
    enabled = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

**Implementation**: Create tool registry service

---

### Module 4: Managed Runtime Governance

**Status**: NEW

**Files to Create**:
- `app/governance/runtime_governance.py`

**Entities**:
```python
class RuntimeInstance(Base):
    id = Column(String, primary_key=True)
    runtime_id = Column(String, ForeignKey("runtime.id"))
    status = Column(String)  # healthy, degraded, unavailable
    health_score = Column(Float)
    last_heartbeat = Column(DateTime)
    instance_type = Column(String)  # local, managed, external
```

---

### Module 5: Context Window / Compaction

**Status**: EXISTING (compaction service exists)

**Files**:
- `app/memory/compaction.py`

**Extensions Needed**:
- `context_budget` table
- `compaction_summary` table
- `token_accounting` table

**Implementation**: Add persistence for compaction summaries

---

## Phase 1: Orchestrator v1 Enablement

### Module 6: Policy Governance

**Status**: PARTIAL (existing in claude-coder)

**Files**:
- `services/claude-coder/policy.py`
- `services/claude-coder/policies.yaml`

**Extensions Needed**:
- `policy` table (centralized)
- `policy_version` table
- `policy_attachment` table
- `policy_violation` table

**Implementation**: Extract from claude-coder, make central

---

### Module 7: Guardrails / Privacy / Compliance

**Status**: NEW

**Files to Create**:
- `app/governance/guardrails.py`

**Entities**:
```python
class Guardrail(Base):
    id = Column(String, primary_key=True)
    name = Column(String)
    type = Column(String)  # input, output, context
    config = Column(JSON)
    enabled = Column(Boolean)

class PIIRule(Base):
    id = Column(String, primary_key=True)
    pattern = Column(String)
    action = Column(String)  # mask, block, redact
    severity = Column(String)
```

---

### Module 8: Audit & Evidence

**Status**: PARTIAL (existing in app/core/audit.py)

**Files**:
- `app/core/audit.py`

**Extensions Needed**:
- `audit_log` table (enhance)
- `evidence_record` table
- `audit_trail` table

**Implementation**: Expand audit to cover all modules

---

## Phase 2: Growth Features

### Module 9: Skill Lifecycle & Evaluation

**Status**: NEW

**Files to Create**:
- `app/agents/skills.py`
- `app/models/skill.py`

**Entities**:
```python
class Skill(Base):
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(Text)
    category = Column(String)
    version = Column(String)
    status = Column(String)  # draft, active, deprecated
    
class SkillEvaluation(Base):
    id = Column(String, primary_key=True)
    skill_id = Column(String, ForeignKey("skill.id"))
    metric_name = Column(String)
    metric_value = Column(Float)
    evaluated_at = Column(DateTime)
```

---

### Module 10: Agent Capability Management

**Status**: NEW

**Files to Create**:
- `app/agents/capabilities.py`

**Entities**:
```python
class AgentCapability(Base):
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(Text)
    category = Column(String)

class AgentEntitlement(Base):
    id = Column(String, primary_key=True)
    tenant_id = Column(String, ForeignKey("tenant.id"))
    capability_id = Column(String, ForeignKey("agent_capability.id"))
    quota = Column(Integer)
    used = Column(Integer)
```

---

### Module 11: SLA Governance

**Status**: NEW

**Files to Create**:
- `app/governance/sla.py`

**Entities**:
```python
class SLA(Base):
    id = Column(String, primary_key=True)
    name = Column(String)
    target_type = Column(String)  # response_time, execution_time
    target_value = Column(Integer)
    severity = Column(String)  # critical, high, medium

class SLA Breach(Base):
    id = Column(String, primary_key=True)
    sla_id = Column(String, ForeignKey("sla.id"))
    breached_at = Column(DateTime)
    acknowledged = Column(Boolean)
    resolved_at = Column(DateTime)
```

---

## Phase 3: Enterprise Features

### Module 12-14: Access Control & Governance

**Status**: NEW

**Files to Create**:
- `app/security/access_control.py`
- `app/security/identity.py`

**Entities**:
```python
class Permission(Base):
    id = Column(String, primary_key=True)
    name = Column(String)
    resource = Column(String)
    action = Column(String)

class Role(Base):
    id = Column(String, primary_key=True)
    name = Column(String)
    permissions = Column(JSON)

class Identity(Base):
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user.id"))
    identity_provider = Column(String)
    external_id = Column(String)
```

---

### Module 15: Policy Packs

**Status**: NEW

**Files to Create**:
- `app/governance/policy_packs.py`

**Entities**:
```python
class PolicyPack(Base):
    id = Column(String, primary_key=True)
    name = Column(String)  # SOC2, HIPAA, GDPR
    description = Column(Text)
    version = Column(String)
    
class CompliancePack(Base):
    id = Column(String, primary_key=True)
    name = Column(String)
    framework = Column(String)
    requirements = Column(JSON)
```

---

### Module 16-24: Business Modules

Post-orchestrator enterprise features.

---

## Implementation Priority Matrix

| Priority | Module | Dependencies | Est. Effort |
|----------|--------|--------------|-------------|
| P0 | Runtime Registry | None | 1 day |
| P0 | Channel/Branch/Worker | 1 | 2 days |
| P0 | Tool Registry | 1 | 2 days |
| P0 | Runtime Governance | 1 | 1 day |
| P0 | Context Compaction | 1, 2 | 1 day |
| P1 | Policy Governance | P0 | 3 days |
| P1 | Guardrails | 6 | 2 days |
| P1 | Audit & Evidence | 6, 7 | 2 days |
| P2 | Skill Lifecycle | P0, P1 | 3 days |
| P2 | Agent Capabilities | P0, P1 | 2 days |
| P2 | SLA Governance | P1 | 2 days |
| P3 | Access Control | P1 | 5 days |
| P3 | Identity Governance | 12 | 3 days |
| P3 | Data Governance | 7, 8 | 3 days |

---

## Next Steps

1. Begin Phase 0 implementation
2. Extend runtime registry with instance tracking
3. Add tool registry service
4. Continue with Phase 1 as orchestrator takes shape

---

_End of Module Roadmap v2_