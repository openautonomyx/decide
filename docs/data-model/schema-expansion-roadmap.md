# Schema Expansion Roadmap

This document provides the detailed data model roadmap for schema expansion, organized by implementation priority.

---

## Entity Dependency Graph

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CORE ENTITIES (EXISTING)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  tenant    user    employee    execution_request    thread    product     │
│  project   group   task        milestone            reminder  approval     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 0: RUNTIME FOUNDATION                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  runtime ──────► runtime_capability ──────► runtime_selection_policy       │
│                                                                      │
│  channel ──────► branch ──────► worker ──────► cortex_context             │
│                                                                      │
│  tool ──────► tool_version ──────► tool_category ──────► tool_governance  │
│                                                                      │
│  runtime_instance ──────► runtime_health ──────► runtime_metrics        │
│                                                                      │
│  context_budget ──────► compaction_summary ──────► token_accounting     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 1: GOVERNANCE LAYER                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  policy ──────► policy_version ──────► policy_attachment ──► policy_viol│
│                                                                      │
│  guardrail ──────► guardrail_config ──────► pii_rule ──► compliance_ctrl │
│                                                                      │
│  audit_log ──────► evidence_record ──────► audit_trail                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 2: GROWTH EXTENSIONS                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  skill ──────► skill_version ──────► skill_evaluation ──► skill_training  │
│                                                                      │
│  agent_capability ──────► agent_entitlement ──────► agent_quota          │
│                                                                      │
│  sla ──────► sla_breach ──────► sla_remediation                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 3: ENTERPRISE SCALE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  permission ──────► role ──────► role_permission ──► user_role            │
│                                                                      │
│  access_review ──────► access_review_item ──► access_review_result      │
│                                                                      │
│  identity ──────► identity_provider ──────► provisioning_rule            │
│                                                                      │
│  data_classification ──────► data_lineage ─────► retention_policy        │
│                                                                      │
│  policy_pack ──────► compliance_pack ──────► pack_mapping              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 0: Runtime Foundation Entities

### Core Runtime Entities

```python
# runtime table - extends existing
class Runtime(Base):
    __tablename__ = "runtime"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50))  # langgraph, openai_agents, claude_agent, etc.
    description = Column(Text)
    
    # Capabilities
    max_context_tokens = Column(Integer, default=200000)
    supports_streaming = Column(Boolean, default=False)
    supports_tools = Column(Boolean, default=True)
    supports_checkpoint = Column(Boolean, default=False)
    
    # Status
    status = Column(String(20), default="active")
    enabled = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


# runtime_capability table
class RuntimeCapability(Base):
    __tablename__ = "runtime_capability"
    
    id = Column(String(36), primary_key=True)
    runtime_id = Column(String(36), ForeignKey("runtime.id"))
    
    tag = Column(String(50))  # coding, conversation, autonomous, etc.
    description = Column(Text)
    max_tokens = Column(Integer)
    
    # Pricing
    input_cost_per_1k = Column(Float, default=0.0)
    output_cost_per_1k = Column(Float, default=0.0)


# runtime_selection_policy table
class RuntimeSelectionPolicy(Base):
    __tablename__ = "runtime_selection_policy"
    
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenant.id"))
    
    task_type = Column(String(50))  # coding, conversation, etc.
    preferred_runtime_id = Column(String(36), ForeignKey("runtime.id"))
    fallback_order = Column(JSON)  # list of runtime IDs
    
    priority = Column(Integer, default=100)
    enabled = Column(Boolean, default=True)
```

### Channel & Branch Entities

```python
# channel table
class Channel(Base):
    __tablename__ = "channel"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100))
    type = Column(String(50))  # web, slack, discord, api
    
    # Configuration
    config = Column(JSON)
    webhook_url = Column(String(500))
    
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# branch table
class Branch(Base):
    __tablename__ = "branch"
    
    id = Column(String(36), primary_key=True)
    thread_id = Column(String(36), ForeignKey("thread.id"))
    channel_id = Column(String(36), ForeignKey("channel.id"))
    
    parent_branch_id = Column(String(36), ForeignKey("branch.id"))
    branch_type = Column(String(20))  # main, fork, merge
    
    # State
    status = Column(String(20))  # active, merged, closed
    metadata = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# worker table
class Worker(Base):
    __tablename__ = "worker"
    
    id = Column(String(36), primary_key=True)
    branch_id = Column(String(36), ForeignKey("branch.id"))
    
    worker_type = Column(String(50))  # execution, tool, review
    
    # Execution context
    runtime_id = Column(String(36), ForeignKey("runtime.id"))
    state = Column(JSON)
    
    status = Column(String(20))  # pending, running, completed, failed
    
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
```

### Tool Registry Entities

```python
# tool table
class Tool(Base):
    __tablename__ = "tool"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50))
    description = Column(Text)
    
    # Versioning
    version = Column(String(20))
    status = Column(String(20))  # draft, active, deprecated
    
    # Definition
    schema = Column(JSON)  # OpenAI tool schema
    handler = Column(String(200))  # module.path
    
    # Governance
    requires_approval = Column(Boolean, default=False)
    risk_level = Column(String(20))  # low, medium, high, critical
    
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# tool_governance_policy table
class ToolGovernancePolicy(Base):
    __tablename__ = "tool_governance_policy"
    
    id = Column(String(36), primary_key=True)
    tool_id = Column(String(36), ForeignKey("tool.id"))
    
    policy_type = Column(String(50))  # usage_limit, requires_approval, etc.
    config = Column(JSON)
    
    enabled = Column(Boolean, default=True)
```

### Runtime Governance Entities

```python
# runtime_instance table
class RuntimeInstance(Base):
    __tablename__ = "runtime_instance"
    
    id = Column(String(36), primary_key=True)
    runtime_id = Column(String(36), ForeignKey("runtime.id"))
    
    instance_type = Column(String(50))  # local, managed, external
    endpoint = Column(String(500))
    
    # Health
    status = Column(String(20))  # healthy, degraded, unavailable
    health_score = Column(Float, default=100.0)
    last_heartbeat = Column(DateTime)
    
    # Metrics
    avg_latency_ms = Column(Integer, default=0)
    success_rate = Column(Float, default=100.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# runtime_metrics table
class RuntimeMetrics(Base):
    __tablename__ = "runtime_metrics"
    
    id = Column(String(36), primary_key=True)
    instance_id = Column(String(36), ForeignKey("runtime_instance.id"))
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Usage
    requests_count = Column(Integer, default=0)
    tokens_input = Column(Integer, default=0)
    tokens_output = Column(Integer, default=0)
    
    # Performance
    avg_latency_ms = Column(Integer, default=0)
    p99_latency_ms = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
```

### Context Compaction Entities

```python
# context_budget table
class ContextBudget(Base):
    __tablename__ = "context_budget"
    
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenant.id"))
    
    task_type = Column(String(50))
    input_budget_tokens = Column(Integer, default=150000)
    output_budget_tokens = Column(Integer, default=50000)
    
    compaction_threshold = Column(Float, default=0.8)


# compaction_summary table
class CompactionSummary(Base):
    __tablename__ = "compaction_summary"
    
    id = Column(String(36), primary_key=True)
    thread_id = Column(String(36), ForeignKey("thread.id"))
    tenant_id = Column(String(36), ForeignKey("tenant.id"))
    
    # Summary content
    running_summary = Column(Text)
    open_loops = Column(JSON)  # list of open items
    
    # Token accounting
    tokens_before = Column(Integer)
    tokens_after = Column(Integer)
    tokens_saved = Column(Integer)
    
    step = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## Phase 1: Governance Layer Entities

### Policy Entities

```python
# policy table (centralized)
class Policy(Base):
    __tablename__ = "policy"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50))  # routing, execution, approval
    description = Column(Text)
    
    # Versioning
    version = Column(String(20))
    status = Column(String(20))  # draft, active, deprecated
    
    # Rules
    conditions = Column(JSON)  # when clause
    actions = Column(JSON)  # use, fallback_order
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


# policy_violation table
class PolicyViolation(Base):
    __tablename__ = "policy_violation"
    
    id = Column(String(36), primary_key=True)
    policy_id = Column(String(36), ForeignKey("policy.id"))
    
    execution_request_id = Column(String(36), ForeignKey("execution_request.id"))
    tenant_id = Column(String(36), ForeignKey("tenant.id"))
    
    violation_type = Column(String(50))
    details = Column(JSON)
    
    acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Guardrail Entities

```python
# guardrail table
class Guardrail(Base):
    __tablename__ = "guardrail"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100))
    type = Column(String(50))  # input, output, context
    
    config = Column(JSON)
    enabled = Column(Boolean, default=True)


# pii_rule table
class PIIRule(Base):
    __tablename__ = "pii_rule"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100))
    pattern = Column(String(200))  # regex or pattern
    
    action = Column(String(50))  # mask, block, redact
    severity = Column(String(20))  # low, medium, high
    
    enabled = Column(Boolean, default=True)
```

### Audit Entities

```python
# audit_log table (enhanced)
class AuditLog(Base):
    __tablename__ = "audit_log"
    
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenant.id"))
    
    # Actor
    user_id = Column(String(36), ForeignKey("user.id"))
    
    # Action
    action = Column(String(100))
    resource_type = Column(String(50))
    resource_id = Column(String(36))
    
    # Details
    changes = Column(JSON)
    metadata = Column(JSON)
    
    # Evidence
    evidence_id = Column(String(36), ForeignKey("evidence_record.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)


# evidence_record table
class EvidenceRecord(Base):
    __tablename__ = "evidence_record"
    
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenant.id"))
    
    evidence_type = Column(String(50))  # screenshot, log, transcript
    content = Column(Text)
    checksum = Column(String(64))
    
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## Phase 2: Growth Extension Entities

### Skill Entities

```python
# skill table
class Skill(Base):
    __tablename__ = "skill"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(Text)
    category = Column(String(50))
    
    version = Column(String(20))
    status = Column(String(20))  # draft, active, deprecated
    
    # Definition
    definition = Column(JSON)
    training_data_id = Column(String(36))
    
    created_at = Column(DateTime, default=datetime.utcnow)


# skill_evaluation table
class SkillEvaluation(Base):
    __tablename__ = "skill_evaluation"
    
    id = Column(String(36), primary_key=True)
    skill_id = Column(String(36), ForeignKey("skill.id"))
    
    metric_name = Column(String(50))
    metric_value = Column(Float)
    benchmark_value = Column(Float)
    
    evaluated_at = Column(DateTime, default=datetime.utcnow)
```

### Agent Capability Entities

```python
# agent_capability table
class AgentCapability(Base):
    __tablename__ = "agent_capability"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100))
    description = Column(Text)
    category = Column(String(50))


# agent_entitlement table
class AgentEntitlement(Base):
    __tablename__ = "agent_entitlement"
    
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenant.id"))
    capability_id = Column(String(36), ForeignKey("agent_capability.id"))
    
    quota = Column(Integer)  # -1 for unlimited
    used = Column(Integer, default=0)
    
    period = Column(String(20))  # daily, monthly, yearly
    period_start = Column(DateTime)
```

### SLA Entities

```python
# sla table
class SLA(Base):
    __tablename__ = "sla"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100))
    
    target_type = Column(String(50))  # response_time, execution_time
    target_value = Column(Integer)  # milliseconds
    
    severity = Column(String(20))  # critical, high, medium
    
    tenant_id = Column(String(36), ForeignKey("tenant.id"))
    enabled = Column(Boolean, default=True)


# sla_breach table
class SLABreach(Base):
    __tablename__ = "sla_breach"
    
    id = Column(String(36), primary_key=True)
    sla_id = Column(String(36), ForeignKey("sla.id"))
    
    breached_at = Column(DateTime)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(36), ForeignKey("user.id"))
    acknowledged_at = Column(DateTime)
    
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
```

---

## Phase 3: Enterprise Scale Entities

### Access Control Entities

```python
# permission table
class Permission(Base):
    __tablename__ = "permission"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100))
    resource = Column(String(100))
    action = Column(String(50))


# role table
class Role(Base):
    __tablename__ = "role"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100))
    description = Column(Text)
    permissions = Column(JSON)  # list of permission IDs
    
    tenant_id = Column(String(36), ForeignKey("tenant.id"))
    is_system = Column(Boolean, default=False)


# user_role table
class UserRole(Base):
    __tablename__ = "user_role"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("user.id"))
    role_id = Column(String(36), ForeignKey("role.id"))
    
    granted_by = Column(String(36), ForeignKey("user.id"))
    granted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
```

### Identity Entities

```python
# identity table
class Identity(Base):
    __tablename__ = "identity"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("user.id"))
    
    identity_provider = Column(String(50))  # okta, azuread, google
    external_id = Column(String(200))
    
    # Profile
    email = Column(String(200))
    display_name = Column(String(100))
    
    # Status
    status = Column(String(20))  # active, suspended
    verified = Column(Boolean, default=False)


# identity_provider table
class IdentityProvider(Base):
    __tablename__ = "identity_provider"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100))
    type = Column(String(50))
    
    config = Column(JSON)  # SSO config
    enabled = Column(Boolean, default=True)
```

### Data Governance Entities

```python
# data_classification table
class DataClassification(Base):
    __tablename__ = "data_classification"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100))  # public, internal, confidential, restricted
    description = Column(Text)
    
    color_code = Column(String(7))  # hex color
    priority = Column(Integer, default=0)


# data_lineage table
class DataLineage(Base):
    __tablename__ = "data_lineage"
    
    id = Column(String(36), primary_key=True)
    source_type = Column(String(50))
    source_id = Column(String(36))
    target_type = Column(String(50))
    target_id = Column(String(36))
    
    transform = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## Implementation Order Summary

| Phase | Tables | Priority | Dependencies |
|-------|--------|----------|--------------|
| 0 | runtime, runtime_capability, runtime_selection_policy | P0 | None |
| 0 | channel, branch, worker | P0 | 1 |
| 0 | tool, tool_governance_policy | P0 | 1 |
| 0 | runtime_instance, runtime_metrics | P0 | 1 |
| 0 | context_budget, compaction_summary | P0 | 1, 2 |
| 1 | policy, policy_violation | P1 | 0 |
| 1 | guardrail, pii_rule | P1 | 1 |
| 1 | audit_log, evidence_record | P1 | 1, 1.1 |
| 2 | skill, skill_evaluation | P2 | 0, 1 |
| 2 | agent_capability, agent_entitlement | P2 | 0, 1 |
| 2 | sla, sla_breach | P2 | 1 |
| 3 | permission, role, user_role | P3 | 1 |
| 3 | identity, identity_provider | P3 | 3 |
| 3 | data_classification, data_lineage | P3 | 1.1 |

---

## Next Steps

1. Review entity definitions
2. Begin Phase 0 table creation
3. Add migrations for new tables

---

_End of Schema Expansion Roadmap_