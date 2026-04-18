# Execution Request State Machine

## States

| State | Description | Terminal? |
|-------|------------|-----------|
| `pending` | Request created, awaiting routing | No |
| `routed` | Backend selected | No |
| `running` | Execution in progress | No |
| `success` | Execution completed successfully | **Yes** |
| `error` | Execution failed | **Yes** |
| `cancelled` | Request cancelled | **Yes** |

## State Diagram

```
[pending] → [routed] → [running] → [success]
                  ↘                ↗
                 [error]           [cancelled]
```

## Transitions

| From | To | Trigger | Driven By |
|-------|-----|---------|----------|
| pending | routed | Backend selected | System |
| pending | cancelled | Human cancels | Human |
| routed | running | Start execution | System |
| routed | cancelled | Human cancels | Human |
| running | success | Execution completes | System |
| running | error | Execution fails | System |

## Terminal States
- `success` - Completed successfully
- `error` - Failed with error
- `cancelled` - Cancelled by human

## Example Triggers

| Trigger | Condition | Action |
|---------|----------|--------|
| Create request | POST /invoke | pending |
| Route | Policy resolves backend | pending → routed |
| Execute | Call backend | routed → running |
| Success | 200 response | running → success |
| Error | Error response | running → error |
| Cancel | Human cancels | * → cancelled |

## Human vs Rule vs System Driven

- **Human-driven**: Create request, cancel request
- **Rule-driven**: Route based on policy
- **System-driven**: Execute, success/error detection