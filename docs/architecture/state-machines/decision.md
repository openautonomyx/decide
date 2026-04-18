# Decision Record State Machine

## States

| State | Description | Terminal? |
|-------|------------|-----------|
| `approved_by_rule` | Approved by policy rules | **Yes** |
| `rejected_by_rule` | Rejected by policy rules | **Yes** |
| `awaiting_human` | Needs human decision | No |
| `approved_by_human` | Human approved | **Yes** |
| `rejected_by_human` | Human rejected | **Yes** |

## State Diagram

```
[approved_by_rule] ──────────────────→ TERMINAL
[rejected_by_rule]  ─────────────────→ TERMINAL
[awaiting_human] → [approved_by_human] → TERMINAL
      ↓
   [rejected_by_human] → TERMINAL
```

## Transitions

| From | To | Trigger | Driven By |
|-------|-----|---------|----------|
| (rule eval) | approved_by_rule | Policy allows | Rule |
| (rule eval) | rejected_by_rule | Policy denies | Rule |
| (rule eval) | awaiting_human | Policy requires human | Rule |
| awaiting_human | approved_by_human | Human approves | Human |
| awaiting_human | rejected_by_human | Human rejects | Human |

## Terminal States
- All states are terminal except `awaiting_human`

## Example Triggers

| Trigger | Condition | Action |
|---------|----------|--------|
| Evaluate policy | Submit execution | Rule eval → approved/rejected/awaiting |
| Approve | Human approves request | awaiting_human → approved_by_human |
| Reject | Human rejects request | awaiting_human → rejected_by_human |

## Human vs Rule vs System Driven

- **Human-driven**: approve_by_human, reject_by_human
- **Rule-driven**: approved_by_rule, rejected_by_rule, awaiting_human
- **System-driven**: Policy evaluation trigger