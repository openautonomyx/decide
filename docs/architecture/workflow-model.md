# Workflow Model

This document finalizes the workflow entity model, explaining why each is first-class.

---

## Overview: First-Class Entities

Each workflow entity serves a distinct purpose and should not be merged:

| Entity | Purpose | Schema Table |
|--------|---------|--------------|
| task | Atomic unit of work | task |
| task_dependency | Dependency relationships | task_dependency |
| task_assignment_history | Audit trail | task_assignment_history |
| deadline | Due dates | deadline |
| milestone | Progress checkpoints | milestone |
| milestone_task | Milestone-task links | milestone_task |
| reminder | Notification triggers | reminder |
| escalation | Risk/issue escalation | escalation |
| task_comment | Discussion | task_comment |
| task_attachment | File attachments | task_attachment |
| task_rating | Quality metrics | task_rating |
| task_feedback | Written feedback | task_feedback |

---

## Task

### Why First-Class?
- Atomic unit of work
- Can be assigned to employee OR agent
- Has status lifecycle
- Can have multiple dependencies
- Links to project and goals

### Schema
| Field | Type |
|-------|------|
| id | VARCHAR(36) |
| tenant_id | VARCHAR(36) |
| project_id | VARCHAR(36) |
| title | VARCHAR(255) |
| description | TEXT |
| status | VARCHAR(50) |
| priority | VARCHAR(20) |
| assigned_to_employee_id | VARCHAR(36) |
| assigned_to_agent_id | VARCHAR(36) |

---

## Task Dependency

### Why First-Class?
- Tracks relationships between tasks
- Enables Gantt/roadmap views
- Required for critical path analysis
- Not a property of task (many-to-many)

### Schema
| Field | Type |
|-------|------|
| id | VARCHAR(36) |
| task_id | VARCHAR(36) |
| depends_on_task_id | VARCHAR(36) |
| dependency_type | VARCHAR(50) |

---

## Task Assignment History

### Why First-Class?
- Audit trail of ownership changes
- Required for accountability
- Enables "who did what when"
- Not a current-state property

### Schema
| Field | Type |
|-------|------|
| id | VARCHAR(36) |
| task_id | VARCHAR(36) |
| assigned_from_type | VARCHAR(20) |
| assigned_from_id | VARCHAR(36) |
| assigned_to_type | VARCHAR(20) |
| assigned_to_id | VARCHAR(36) |
| assigned_by | VARCHAR(36) |

---

## Deadline

### Why First-Class?
- Multiple deadlines per task
- Different from task end date
- Triggers reminders
- Tracks SLA compliance

### Schema
| Field | Type |
|-------|------|
| id | VARCHAR(36) |
| task_id | VARCHAR(36) |
| due_at | TIMESTAMP |
| reminder_at | TIMESTAMP |

---

## Milestone

### Why First-Class?
- Named progress checkpoint
- Groups multiple tasks
- Tracks phase completion
- Has target date

### Schema
| Field | Type |
|-------|------|
| id | VARCHAR(36) |
| project_id | VARCHAR(36) |
| name | VARCHAR(255) |
| target_date | DATE |

---

## Milestone Task

### Why First-Class?
- Many-to-many relationship
- Task can be in multiple milestones
- Milestone can have multiple tasks

### Schema
| Field | Type |
|-------|------|
| id | VARCHAR(36) |
| milestone_id | VARCHAR(36) |
| task_id | VARCHAR(36) |

---

## Reminder

### Why First-Class?
- Entity-agnostic (task/milestone/thread)
- Scheduled notifications
- Can be snoozed
- Not part of task lifecycle

### Schema
| Field | Type |
|-------|------|
| id | VARCHAR(36) |
| reminder_type | VARCHAR(50) |
| entity_type | VARCHAR(50) |
| entity_id | VARCHAR(36) |
| remind_at | TIMESTAMP |
| message | TEXT |

---

## Escalation

### Why First-Class?
- Risk/issue notification
- Different from task status
- Has own lifecycle
- Can escalate to specific employee

### Schema
| Field | Type |
|-------|------|
| id | VARCHAR(36) |
| entity_type | VARCHAR(50) |
| entity_id | VARCHAR(36) |
| escalation_type | VARCHAR(50) |
| reason | TEXT |
| escalated_to_employee_id | VARCHAR(36) |
| status | VARCHAR(50) |

---

## Task Comments & Attachments

### Why First-Class?
- task_comment: Discussion thread
- task_attachment: Direct file to task
- task_comment_attachment: File linked to comment

### Schema
| Table | Purpose |
|-------|---------|
| task_comment | Discussion on task |
| task_attachment | File on task |
| task_comment_attachment | File on comment |

---

## Task Rating & Feedback

### Why First-Class?
- task_rating: Structured metrics (quality/speed/usefulness/clarity)
- task_feedback: Written feedback
- Enables performance analytics

### Schema
| Table | Fields |
|-------|---------|
| task_rating | rating_type, score, rated_by |
| task_feedback | content, provided_by |

---

## End-to-End Example

### Scenario: New Feature Development

```json
{
  "project": {
    "id": "proj-q2-dashboard",
    "name": "Q2 Dashboard Redesign"
  },
  
  "milestone": {
    "id": "milestone-001",
    "project_id": "proj-q2-dashboard",
    "name": "Design Complete",
    "target_date": "2025-04-30"
  },
  
  "tasks": [
    {
      "id": "task-001",
      "title": "Create wireframes",
      "status": "completed",
      "assigned_to_employee_id": "emp-123",
      "milestones": ["milestone-001"]
    },
    {
      "id": "task-002", 
      "title": "Build prototype",
      "status": "in_progress",
      "assigned_to_agent_id": "agt-design-001",
      "dependencies": ["task-001"]
    }
  ],
  
  "deadlines": [
    {
      "task_id": "task-002",
      "due_at": "2025-04-25T17:00:00Z",
      "reminder_at": "2025-04-24T09:00:00Z"
    }
  ],
  
  "comments": [
    {
      "id": "comment-001",
      "task_id": "task-002",
      "author_type": "employee",
      "author_id": "emp-123",
      "content": "Updated the color scheme based on feedback"
    }
  ],
  
  "attachments": [
    {
      "comment_id": "comment-001",
      "file_asset_id": "file-001"
    }
  ],
  
  "reminders": [
    {
      "entity_type": "task",
      "entity_id": "task-002",
      "reminder_type": "deadline",
      "remind_at": "2025-04-24T09:00:00Z",
      "message": "Task deadline approaching"
    }
  ],
  
  "escalations": [
    {
      "entity_type": "task",
      "entity_id": "task-002",
      "escalation_type": "risk_increase",
      "reason": "Blocked by missing API specs",
      "escalated_to_employee_id": "emp-456",
      "status": "open"
    }
  ],
  
  "completion": {
    "ratings": [
      {
        "task_id": "task-001",
        "rating_type": "quality",
        "score": 5,
        "rated_by_employee_id": "emp-456"
      }
    ],
    "feedback": [
      {
        "task_id": "task-001",
        "content": "Great work on the wireframes!",
        "provided_by_employee_id": "emp-456"
      }
    ]
  }
}
```

---

## Relationship to Goals and Timelines

| Workflow Entity | Links To |
|----------------|----------|
| task | project, goal, timeline |
| milestone | project |
| deadline | task |
| reminder | task, milestone, thread |
| escalation | task |

---

## Schema Gaps Found

| Gap | Recommendation |
|-----|---------------|
| Nested comments | Not currently modeled (comments are flat) |
| task_custom_fields | Could add JSONB for extensibility |

---

## Key Design Rules

1. **Each entity first-class** - Don't merge into generic "item"
2. **Task can have multiple deadlines** - Not just one end date
3. **Dependencies are explicit** - Via task_dependency table
4. **Assignment history tracked** - For audit trail
5. **Comments ≠ attachments** - Separate tables
6. **Rating ≠ feedback** - Structured vs unstructured