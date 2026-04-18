# Escalation State Machine

## States

| State | Description | Terminal? |
|-------|------------|-----------|
| `open` | Escalation created, unresolved | No |
| `acknowledged` | Escalation acknowledged | No |
| `in_progress` | Working on resolution | No |
| `resolved` | Escalation resolved | **Yes** |
| `won't_fix` | Won't address escalation | **Yes** |

## State Diagram

```
[open] → [acknowledged] → [in_progress] → [resolved]
    ↓                                    ↑
    └────────── [won't_fix] ←───────────┘
```

## Transitions

| From | To | Trigger | Driven By |
|-------|-----|---------|----------|
| open | acknowledged | Acknowledge escalation | Human |
| open | won't_fix | Decide not to fix | Human |
| acknowledged | in_progress | Start work | Human |
| in_progress | resolved | Fix applied | Human |
| in_progress | won't_fix | Decision not to fix | Human |

## Terminal States
- `resolved` - Issue resolved
- `won't_fix` - Won't address

## Escalation Types

| Type | Description |
|------|-------------|
| `missed_deadline` | Deadline missed |
| `blocker` | Task blocked |
| `no_response` | No response from assignee |
| `risk_increase` | Risk level increased |
| `manual` | Manual escalation |

## Example Triggers

| Trigger | Condition | Action |
|---------|----------|--------|
| Create | System detects issue | Any → open |
| Acknowledge | Human acknowledges | open → acknowledged |
| Work | Human starts fix | acknowledged → in_progress |
| Resolve | Human applies fix | in_progress → resolved |
| Won't fix | Human decides no fix | * → won't_fix |

## Human vs Rule vs System Driven

- **Human-driven**: Acknowledge, resolve, won't fix
- **Rule-driven**: Auto-escalate on deadline miss
- **System-driven**: Create escalation on detected issue