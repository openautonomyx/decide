# State Machines Index

This document provides an overview of all state machines in the Autonomyx platform.

## Overview

| Entity | States | Terminal States | Driven By |
|--------|--------|----------------|----------|
| [task](task.md) | pending/assigned/in_progress/completed/blocked/cancelled | completed, cancelled | Human, Rule, System |
| [approval_request](approval.md) | pending/approved/denied/expired | approved, denied, expired | Human, System |
| [decision_record](decision.md) | approved_by_rule/rejected_by_rule/awaiting_human/approved_by_human/rejected_by_human | All except awaiting | Human, Rule |
| [override_record](override.md) | active/expired/revoked | expired, revoked | Human, System |
| [responsibility_assignment](responsibility-assignment.md) | pending/active/completed/revoked | completed, revoked | Human, System |
| [execution_request](execution-request.md) | pending/routed/running/success/error/cancelled | success, error, cancelled | Human, Rule, System |
| [escalation](escalation.md) | open/acknowledged/in_progress/resolved/won't_fix | resolved, won't_fix | Human, Rule, System |
| [reminder](reminder.md) | scheduled/sent/acknowledged/snoozed/cancelled | acknowledged, cancelled | Human, System |

## State Categories

### Human-Driven
- task (assignment, completion, cancellation)
- approval_request (approve, deny)
- decision_record (approve_by_human, reject_by_human)
- override_record (apply, revoke)
- responsibility_assignment (propose, accept, decline, complete)
- execution_request (create, cancel)
- escalation (acknowledge, resolve, won't_fix)
- reminder (create, acknowledge, snooze, cancel)

### Rule-Driven
- task (auto-block, auto-complete)
- approval_request (auto-expire)
- decision_record (approved_by_rule, rejected_by_rule, awaiting_human)
- execution_request (route)
- escalation (auto-escalate)

### System-Driven
- task (timeout detection)
- approval_request (SLA timeout)
- override_record (expire on time)
- execution_request (execute, success/error detection)
- escalation (detect issue)
- reminder (send at scheduled time)

## Terminal State Patterns

All state machines have clear terminal states where no further transitions occur:

| Entity | Terminal States |
|--------|-------------|
| task | COMPLETED, CANCELLED |
| approval | APPROVED, DENIED, EXPIRED |
| decision | APPROVED_BY_*, REJECTED_BY_* |
| override | EXPIRED, REVOKED |
| responsibility | COMPLETED, REVOKED |
| execution | SUCCESS, ERROR, CANCELLED |
| escalation | RESOLVED, WON'T_FIX |
| reminder | ACKNOWLEDGED, CANCELLED |

## Pause/Resume Semantics

| Entity | Pause | Resume |
|--------|-------|--------|
| task | BLOCKED | IN_PROGRESS |
| execution | (none) | (none) |
| reminder | SNOOZED | SENT |

## Quick Reference

```python
# Allowed transitions (simplified)
TASK_TRANSITIONS = {
    "pending": ["assigned", "cancelled"],
    "assigned": ["in_progress", "cancelled"],
    "in_progress": ["completed", "blocked", "cancelled"],
    "blocked": ["in_progress", "cancelled"],
    "completed": [],
    "cancelled": [],
}

APPROVAL_TRANSITIONS = {
    "pending": ["approved", "denied", "expired"],
    "approved": [],
    "denied": ["pending"],  # Can resubmit
    "expired": [],
}

EXECUTION_TRANSITIONS = {
    "pending": ["routed", "cancelled"],
    "routed": ["running", "cancelled"],
    "running": ["success", "error"],
    "success": [],
    "error": [],
    "cancelled": [],
}
```