# Reminder State Machine

## States

| State | Description | Terminal? |
|-------|------------|-----------|
| `scheduled` | Reminder scheduled | No |
| `sent` | Reminder sent to user | No |
| `acknowledged` | Reminder acknowledged | **Yes** |
| `snoozed` | Reminder snoozed | No |
| `cancelled` | Reminder cancelled | **Yes** |

## State Diagram

```
[scheduled] → [sent] → [acknowledged]
      ↓            ↗
    [snoozed] ───→ [sent]
      ↓
  [cancelled]
```

## Transitions

| From | To | Trigger | Driven By |
|-------|-----|---------|----------|
| scheduled | sent | Reminder time reached | System |
| scheduled | cancelled | Human cancels | Human |
| sent | acknowledged | User acknowledges | Human |
| sent | snoozed | User snoozes | Human |
| snoozed | sent | Snooze time reached | System |
| snoozed | cancelled | Human cancels | Human |

## Terminal States
- `acknowledged` - User acknowledged
- `cancelled` - Cancelled

## Reminder Types

| Type | Description |
|------|-------------|
| `deadline` | Deadline reminder |
| `checkin` | Check-in reminder |
| `followup` | Follow-up reminder |
| `approval` | Approval reminder |

## Example Triggers

| Trigger | Condition | Action |
|---------|----------|--------|
| Create | Set reminder time | Any → scheduled |
| Time reached | reminder_at reached | scheduled → sent |
| Acknowledge | User acknowledges | sent → acknowledged |
| Snooze | User snoozes | sent → snoozed |
| Cancel | Human cancels | * → cancelled |

## Human vs Rule vs System Driven

- **Human-driven**: Create, acknowledge, snooze, cancel
- **Rule-driven**: (none)
- **System-driven**: Send at scheduled time, auto-snooze