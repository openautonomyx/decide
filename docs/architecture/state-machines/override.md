# Override Record State Machine

## States

| State | Description | Terminal? |
|-------|------------|-----------|
| `active` | Override currently in effect | No |
| `expired` | Override expired (time-based) | **Yes** |
| `revoked` | Override manually revoked | **Yes** |

## State Diagram

```
[active] → [expired]
    ↓
[revoked]
```

## Transitions

| From | To | Trigger | Driven By |
|-------|-----|---------|----------|
| active | expired | End time reached | System |
| active | revoke | Human revokes override | Human |

## Terminal States
- `expired` - Override time-based end
- `revoked` - Manually stopped

## Override Types

| Type | Description |
|------|-------------|
| `force_backend` | Force specific backend |
| `bypass_approval` | Skip approval check |
| `allow_exception` | Allow normally denied |
| `change_deadline` | Modify deadline |
| `change_goal` | Modify goal |

## Example Triggers

| Trigger | Condition | Action |
|---------|----------|--------|
| Apply override | Admin applies override | Any → active |
| Time expires | Override end_time reached | active → expired |
| Revoke | Admin revokes override | active → revoked |

## Human vs Rule vs System Driven

- **Human-driven**: Apply override, revoke override
- **Rule-driven**: (none)
- **System-driven**: Expire based on time