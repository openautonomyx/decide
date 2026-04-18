# Control Plane Model

This document finalizes the decision and control plane, preserving critical distinctions.

---

## Core Entities

| Entity | Purpose | Schema Table |
|--------|---------|--------------|
| execution_request | Work request | execution_request |
| execution_request_metadata | Request context | execution_request_metadata |
| execution_history | Audit trail | execution_history |
| policy_resolution | Policy eval result | policy_resolution |
| backend_selection | Backend routing | backend_selection |
| fallback_event | Fallback attempts | fallback_event |
| approval_request | Human approval | approval_request |
| decision_record | Rule decision | decision_record |
| override_record | Override applied | override_record |
| responsibility_assignment | Authority transfer | responsibility_assignment |
| usage_record | Cost/tracking | usage_record |
| memory_checkpoint | State snapshot | memory_checkpoint |
| tenant_policy | Tenant rules | tenant_policy |

---

## Distinction 1: Human Approval vs Rule Decision

### Human Approval
- Request creates `approval_request` entity
- Goes to human inbox
- Human makes decision (approve/deny)
- Creates audit trail

### Rule Decision
- Happens inline during policy evaluation
- Creates `decision_record` immediately
- No human involved unless rule says "awaiting_human"

### Schema Evidence
```sql
-- Human approval (separate entity)
CREATE TABLE approval_request (
    id, status, approver, approver_notes, requested_at, decided_at
);

-- Rule decision (separate entity)
CREATE TABLE decision_record (
    id, execution_request_id, decision_type, decision_reason
);
```

---

## Distinction 2: Default vs Override vs Effective

### Default Decision
- Original policy resolution
- Stored in `policy_resolution`

### Override Applied
- Override record overwrites default
- Stored in `override_record`

### Effective Decision
- Combined result in execution context
- Computed, not stored

### Schema Evidence
```sql
-- Default
CREATE TABLE policy_resolution (
    id, execution_request_id, policy_id, default_decision
);

-- Override  
CREATE TABLE override_record (
    id, execution_request_id, override_type, effective_from, effective_to
);
```

---

## Distinction 3: Delegation vs Acting Authority vs Ownership Transfer

### Delegation
- Temporary authority transfer
- Time-bounded (effective_from/to)

### Acting Authority
- Acting in another role
- Not permanent

### Ownership Transfer
- Permanent change
- One entity takes ownership

### Schema Evidence
```sql
CREATE TABLE responsibility_assignment (
    id, assignment_type, from_type, from_id, to_type, to_id,
    effective_from, effective_to
);
-- assignment_type: delegation | acting_authority | ownership_transfer
```

---

## Distinction 4: Backend Selection vs Fallback vs Actually Used

### Backend Selection
- Policy resolves preferred backend
- Stored in `backend_selection`

### Fallback Event
- When primary fails, fallback triggered
- Stored in `fallback_event`

### Backend Actually Used
- Final backend that executed
- Stored in `usage_record`

### Schema Evidence
```sql
-- Selection
CREATE TABLE backend_selection (
    id, execution_request_id, selected_backend, selection_order
);

-- Fallback chain
CREATE TABLE fallback_event (
    id, execution_request_id, from_backend, to_backend, reason
);

-- Final usage
CREATE TABLE usage_record (
    id, execution_request_id, backend_used, model, input_tokens, output_tokens
);
```

---

## Complete Execution Trace Example

### Step 1: Request Created
```json
{
  "id": "exec-001",
  "tenant_id": "ten-acme",
  "goal": "Refactor authentication module",
  "capability": "coding",
  "quality": "premium",
  "status": "pending",
  "created_at": "2025-04-14T10:00:00Z"
}
```

### Step 2: Policy Evaluation (Rule Decision)
```json
{
  "id": "decision-001",
  "execution_request_id": "exec-001",
  "decision_type": "rejected_by_rule",
  "decision_reason": "premium_quality_not_allowed_for_employee_level",
  "decided_at": "2025-04-14T10:00:01Z"
}
```

### Step 3: Human Override
```json
{
  "id": "override-001",
  "execution_request_id": "exec-001",
  "override_type": "allow_exception",
  "reason": "Q2 critical delivery",
  "applied_by": "emp-456",
  "effective_from": "2025-04-14T10:00:02Z"
}
```

### Step 4: Effective Approval (via approval_request)
```json
{
  "id": "approval-001",
  "execution_request_id": "exec-001",
  "status": "approved",
  "approver": "emp-456",
  "approver_notes": "Approved for Q2 delivery",
  "decided_at": "2025-04-14T10:00:03Z"
}
```

### Step 5: Backend Selection
```json
{
  "id": "backend-001",
  "execution_request_id": "exec-001",
  "selected_backend": "claude_premium",
  "selection_order": 1,
  "selected_at": "2025-04-14T10:00:04Z"
}
```

### Step 6: Execution Running
```json
{
  "id": "exec-001",
  "status": "running",
  "started_at": "2025-04-14T10:00:05Z"
}
```

### Step 7: Fallback Event (Premium fails, Lite succeeds)
```json
{
  "id": "fallback-001",
  "execution_request_id": "exec-001",
  "from_backend": "claude_premium",
  "to_backend": "devstral_lite",
  "reason": "rate_limit_exceeded",
  "triggered_at": "2025-04-14T10:00:15Z"
}
```

### Step 8: Execution History
```json
{
  "id": "history-001",
  "execution_request_id": "exec-001",
  "event_type": "fallback_triggered",
  "event_data": {"from": "claude_premium", "to": "devstral_lite"},
  "created_at": "2025-04-14T10:00:15Z"
}
```

### Step 9: Memory Checkpoint Written
```json
{
  "id": "checkpoint-001",
  "execution_request_id": "exec-001",
  "thread_id": "thread-123",
  "checkpoint_data": {"state": "...", "step": 45},
  "created_at": "2025-04-14T10:01:00Z"
}
```

### Step 10: Execution Complete
```json
{
  "id": "exec-001",
  "status": "success",
  "completed_at": "2025-04-14T10:01:30Z"
}
```

### Step 11: Usage Record
```json
{
  "id": "usage-001",
  "execution_request_id": "exec-001",
  "backend_used": "devstral_lite",
  "provider": "openai",
  "model": "devstral-lite",
  "input_tokens": 2500,
  "output_tokens": 1800,
  "total_tokens": 4300,
  "cost_usd": 0.043,
  "latency_ms": 85000
}
```

---

## State Machine Integration

| Entity | States | Driven By |
|--------|--------|----------|
| execution_request | pending/running/success/error | System |
| approval_request | pending/approved/denied | Human |
| decision_record | approved/rejected/awaiting | Rule |
| override_record | active/expired/revoked | Human |
| responsibility | pending/active/completed | Human |

---

## Schema Gaps Found

No gaps identified - all distinctions preserved in schema.

---

## Key Design Rules

1. **Human ≠ Rule** - Separate approval vs decision entities
2. **Override preserved** - Override record tracks what changed
3. **Delegation explicit** - Three types in responsibility_assignment
4. **Fallback traceable** - fallback_event captures chain
5. **Usage recorded** - For cost tracking and analytics