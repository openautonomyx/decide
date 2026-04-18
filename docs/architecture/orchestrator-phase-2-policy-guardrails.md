# Orchestrator Phase 2: Policy and Guardrails

This document describes the Phase 2 policy and guardrail integration for the orchestrator.

---

## Overview

Phase 2 adds governance layers to the orchestrator:

1. **Policy Gate** - Evaluates execution policies before runtime
2. **Guardrails** - Input/output validation and safety checks
3. **Approval Gate** - Human-in-the-loop (HITL) approval workflow

---

## Components

| File | Description |
|------|-------------|
| `app/orchestrator/policy_gate.py` | Policy evaluation (allow/deny/approve/escalate) |
| `app/orchestrator/guardrails.py` | Input/output safety checks |
| `app/orchestrator/approval_gate.py` | HITL approval workflow |

---

## Policy Gate

### Decisions

| Decision | Description |
|----------|-------------|
| `allow` | Proceed with execution |
| `deny` | Block execution |
| `require_approval` | Pause for human approval |
| `escalate` | Route to admin review |

### Default Rules

```python
# High-risk tool requires approval
PolicyDecision.REQUIRE_APPROVAL
  → tool: "execute_code"
  → reason: "High-risk tool requires approval"

# Block destructive commands
PolicyDecision.DENY
  → pattern: "rm -rf|delete all|drop table"
  → reason: "Destructive commands blocked"

# Tenant quota exceeded
PolicyDecision.ESCALATE
  → condition: tenant_quota_exceeded
  → reason: "Tenant quota exceeded"

# Tenant policy denies all
PolicyDecision.DENY
  → condition: tenant_policy: "deny_all"
  → reason: "Tenant policy denies all"
```

### Usage

```python
from app.orchestrator.policy_gate import get_policy_gate, PolicyDecision

gate = get_policy_gate()

result = gate.evaluate(execution_state, orchestrator_request)

if result["decision"] == PolicyDecision.ALLOW:
    # Proceed
elif result["decision"] == PolicyDecision.DENY:
    # Block - return error
elif result["decision"] == PolicyDecision.REQUIRE_APPROVAL:
    # Create approval request
elif result["decision"] == PolicyDecision.ESCALATE:
    # Route to admin
```

---

## Guardrails

### Decisions

| Decision | Description |
|----------|-------------|
| `allow` | Proceed normally |
| `block` | Block the request |
| `mask` | Mask sensitive data |
| `flag` | Flag for review |

### Default Rules

#### Input Guardrails

```python
# Block SSN pattern
GuardrailDecision.BLOCK
  → pattern: r"\b\d{3}-\d{2}-\d{4}\b"
  → reason: "SSN pattern detected"

# Block credit card
GuardrailDecision.BLOCK
  → pattern: r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"
  → reason: "Credit card pattern detected"

# Flag confidential keywords
GuardrailDecision.FLAG
  → keywords: ["confidential", "private key", "api secret"]
  → reason: "Sensitive keyword detected"
```

#### Tool Guardrails

```python
# Block shell execution
GuardrailDecision.BLOCK
  → tool: "shell_exec"

# Block file deletion
GuardrailDecision.BLOCK
  → tool: "delete_file"
```

#### Skill Guardrails

```python
# Flag admin skills
GuardrailDecision.FLAG
  → skill: "admin_access"
```

### Usage

```python
from app.orchestrator.guardrails import get_guardrails, GuardrailDecision

guardrails = get_guardrails()

# Check single input
result = guardrails.check_input("hello world")
# → GuardrailResult(decision=ALLOW)

# Check for SSN
result = guardrails.check_input("SSN: 123-45-6789")
# → GuardrailResult(decision=BLOCK, reason="SSN pattern detected")

# Check tools
results = guardrails.check_tools(["search_web", "shell_exec"])
# → [allow, block]

# Full evaluation
result = guardrails.evaluate(request, tools=["search_web"], skills=["code_review"])
# → {decision: ALLOW, blocked: False, flagged: False}
```

---

## Approval Gate

### Status

| Status | Description |
|--------|-------------|
| `pending` | Awaiting approval |
| `approved` | Approved for execution |
| `rejected` | Rejected |
| `expired` | Timed out |

### Workflow

```
1. Orchestrator detects need for approval
2. Creates ApprovalRequest
3. Returns result with next_action = NEEDS_APPROVAL
4. Human reviews and approves/rejects
5. Orchestrator checks status before execution
6. If approved, proceeds; if rejected, stops
```

### Usage

```python
from app.orchestrator.approval_gate import get_approval_gate, ApprovalStatus

gate = get_approval_gate()

# Create approval request
approval = gate.create_approval_request(
    execution_id="exec-123",
    tenant_id="tenant-456",
    requested_by="user-789",
    reason="High-risk tool execution",
    details={"tool": "execute_code"},
)

# Check status
status = gate.check_approval_status("exec-123")
# → {requires_approval: True, can_proceed: False, status: "pending"}

# Approve
gate.approve(approval.approval_id, "admin-user", "Approved")

# Reject
gate.reject(approval.approval_id, "admin-user", "Risk too high")
```

---

## Integration with Orchestrator

The orchestrator integrates policy/guardrails in these stages:

```
STAGE 8: EXECUTION (Modified)
         │
         ├──→ Policy Gate Evaluation
         │        │
         │        ├── ALLOW → Continue to Guardrails
         │        │
         │        ├── DENY → Return error result
         │        │
         │        ├── REQUIRE_APPROVAL → Create approval request
         │        │                        → Return paused result
         │        │
         │        └── ESCALATE → Route to admin
         │
         └──→ Guardrail Evaluation
                  │
                  ├── ALLOW → Proceed with execution
                  │
                  ├── BLOCK → Return blocked result
                  │
                  └── FLAG → Log and proceed (or pause)
```

---

## Extension Hooks

### OPA Integration (Future)

```python
# Future: External policy engine
def evaluate_with_opa(state, request):
    # Send to OPA
    response = opa_client.evaluate(
        input={
            "state": state.dict(),
            "request": request.dict(),
        }
    )
    return response.decision
```

### Custom Guardrails (Future)

```python
# Future: Custom guardrail registry
def register_guardrail(name, check_function):
    guardrails.register(name, check_function)
```

---

## Test Coverage

Tests are in `tests/test_orchestrator_phase2.py`:

### Policy Gate Tests

- `test_allow_by_default` - Default allow
- `test_block_destructive_pattern` - Block rm -rf
- `test_require_approval_for_high_risk_tool` - Tool approval
- `test_tools_evaluation` - Tool-specific policy
- `test_get_rules` - Rule retrieval

### Guardrail Tests

- `test_allow_clean_input` - Clean input passes
- `test_block_ssn_pattern` - SSN blocked
- `test_block_credit_card` - Credit card blocked
- `test_flag_confidential_keywords` - Keywords flagged
- `test_block_dangerous_tools` - Dangerous tools blocked
- `test_full_evaluation` - Full evaluation

### Approval Gate Tests

- `test_create_approval_request` - Create request
- `test_approve_request` - Approve workflow
- `test_reject_request` - Reject workflow
- `test_check_approval_status_pending` - Pending status
- `test_check_approval_status_approved` - Approved status
- `test_check_approval_status_no_approval` - No approval
- `test_list_pending` - List pending

---

## What Is Real vs Stubbed

| Component | Status | Notes |
|-----------|--------|-------|
| Policy gate rules | ✅ REAL | Rule-based evaluation |
| Policy decisions | ✅ REAL | allow/deny/approve/escalate |
| Guardrail input checks | ✅ REAL | PII pattern detection |
| Guardrail tool checks | ✅ REAL | Tool blocking |
| Guardrail skill checks | ✅ REAL | Skill flagging |
| Approval workflow | ✅ REAL | Create/approve/reject |
| **OPA integration** | 🔶 PLACEHOLDER | Hook exists, not integrated |
| **Custom guardrails** | 🔶 PLACEHOLDER | Registry not implemented |
| **Output guardrails** | 🔶 PLACEHOLDER | Input checks only |

---

## Next Steps (Phase 3)

1. **Runtime Invocation** - Connect to actual runtimes
2. **Compaction Execution** - Run actual context compaction
3. **Audit Logging** - Full audit trail integration
4. **Persistence** - Redis/DB for state
5. **OPA Integration** - External policy engine
6. **Custom Guardrails** - Dynamic guardrail registry

---

_End of Orchestrator Phase 2 Documentation_