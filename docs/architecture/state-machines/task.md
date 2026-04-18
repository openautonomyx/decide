# Task State Machine

## States

| State | Description | Terminal? |
|-------|------------|-----------|
| `pending` | Task created, awaiting assignment | No |
| `assigned` | Task assigned to employee or agent | No |
| `in_progress` | Task actively being worked | No |
| `completed` | Task finished successfully | **Yes** |
| `blocked` | Task blocked by dependency | No |
| `cancelled` | Task cancelled | **Yes** |

## State Diagram

```
[pending] → [assigned] → [in_progress] → [completed]
     ↑                                    ↓
     └──────── [blocked] ←───────────────↑
          ↳ [cancelled] ←───────────────↲
```

## Transitions

| From | To | Trigger | Driven By |
|-------|-----|---------|----------|
| pending | assigned | Assign task to employee/agent | Human |
| assigned | in_progress | Start work on task | Employee/Agent |
| in_progress | completed | Submit task completion | Employee/Agent |
| in_progress | blocked | Mark as blocked | Employee/Agent |
| assigned | in_progress | Begin work (skip assignment) | Employee/Agent |
| blocked | in_progress | Unblock task | Employee/Agent |
| * | cancelled | Cancel task | Human |
| pending | cancelled | Reject task | Human |
| assigned | cancelled | Reject assignment | Human |

## Allowed State Changes

```python
ALLOWED_TRANSITIONS = {
    "pending": ["assigned", "cancelled"],
    "assigned": ["in_progress", "cancelled"],
    "in_progress": ["completed", "blocked", "cancelled"],
    "blocked": ["in_progress", "cancelled"],
    "completed": [],
    "cancelled": [],
}
```

## Terminal States
- `completed` - Task successfully finished
- `cancelled` - Task cancelled (no further action)

## Pause/Resume Semantics
- **Pause**: Task moves to `blocked` or stays `in_progress` with paused_at timestamp
- **Resume**: Task returns to `in_progress` from `blocked`

## Example Triggers

| Trigger | Condition | Action |
|---------|----------|--------|
| Assign task | Human assigns | `pending → assigned` |
| Start work | Employee begins work | `assigned → in_progress` |
| Complete task | Employee submits | `in_progress → completed` |
| Block task | Dependency not ready | `in_progress → blocked` |
| Unblock | Dependency resolved | `blocked → in_progress` |
| Cancel | Human cancels | `* → cancelled` |

## Human vs Rule vs System Driven

- **Human-driven**: Initial assignment, cancellation, blocking decision
- **Rule-driven**: Auto-complete when subtasks done, auto-block on dependency
- **System-driven**: Auto-transition on timeout, reminder triggers