# Approval Request State Machine

## States

| State | Description | Terminal? |
|-------|------------|-----------|
| `pending` | Awaiting approver decision | No |
| `approved` | Approved by approver | **Yes** |
| `denied` | Denied by approver | **Yes** |
| `expired` | No response within SLA | **Yes** |

## State Diagram

```
[pending] → [approved]
     ↓
   [denied]
     ↓
  [expired]
```

## Transitions

| From | To | Trigger | Driven By |
|-------|-----|---------|----------|
| pending | approved | Approver approves | Human |
| pending | denied | Approver denies | Human |
| pending | expired | SLA timeout | System |
| approved | pending | Revoke approval (re-submit) | Human |
| denied | pending | Resubmit request | Human |

## Terminal States
- `approved` - Approval granted
- `denied` - Approval denied
- `expired` - Timed out without decision

## Example Triggers

| Trigger | Condition | Action |
|---------|----------|--------|
| Submit request | Create approval_request | Any → pending |
| Approve | Approver clicks approve | pending → approved |
| Deny | Approver clicks deny | pending → denied |
| Timeout | SLA exceeded | pending → expired |

## Human vs Rule vs System Driven

- **Human-driven**: approve, deny, revoke
- **Rule-driven**: Auto-expire on SLA, auto-remind
- **System-driven**: SLA timeout detection