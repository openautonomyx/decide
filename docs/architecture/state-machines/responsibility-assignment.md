# Responsibility Assignment State Machine

## States

| State | Description | Terminal? |
|-------|------------|-----------|
| `pending` | Assignment proposed, awaiting accept | No |
| `active` | Responsibility transferred | No |
| `completed` | Assignment fulfilled | **Yes** |
| `revoked` | Assignment revoked | **Yes** |

## State Diagram

```
[pending] → [active] → [completed]
    ↓              ↑
    └─────── [revoked] ←─────┘
```

## Transitions

| From | To | Trigger | Driven By |
|-------|-----|---------|----------|
| pending | active | Accept assignment | Human |
| pending | revoked | Decline/revoke | Human |
| active | completed | Task completed | Human/System |
| active | revoked | Revoke authority | Human |

## Terminal States
- `completed` - Assignment fulfilled
- `revoked` - Revoked or declined

## Assignment Types

| Type | Description |
|------|-------------|
| `delegation` | Temporary authority transfer |
| `acting_authority` | Acting in another role |
| `ownership_transfer` | Permanent ownership change |

## Example Triggers

| Trigger | Condition | Action |
|---------|----------|--------|
| Propose | Human proposes delegation | Any → pending |
| Accept | Delegate accepts | pending → active |
| Complete | Task completed | active → completed |
| Revoke | Original owner revokes | active → revoked |
| Decline | Delegate declines | pending → revoked |

## Human vs Rule vs System Driven

- **Human-driven**: Propose, accept, decline, complete, revoke
- **Rule-driven**: Auto-complete on task completion
- **System-driven**: Expire on effective_to date