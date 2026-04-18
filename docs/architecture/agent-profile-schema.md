# Agent Profile Schema

This document defines the complete agent profile model, reflecting the schema accurately.

## Overview

An **agent** is an AI entity that is separate from **employee** (human). The agent profile consists of multiple components spread across schema tables.

---

## Agent Identity / Org Context

Schema tables: `agent`, `agent_identity`, `employee_agent_assignment`, `group_membership`

### Core Agent
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key (UUID) |
| tenant_id | VARCHAR(36) | FK to tenant |
| name | VARCHAR(255) | Agent name |
| agent_type | VARCHAR(50) | Type of agent |
| is_primary | BOOLEAN | Primary human-facing agent |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

### Identity Projection
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| agent_id | VARCHAR(36) | FK to agent |
| projected_title | VARCHAR(255) | Projected job title |
| projected_department | VARCHAR(255) | Projected department |
| effective_from | TIMESTAMP | Effective from date |
| effective_to | Effective to date |

### Ownership / Supervision
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| employee_id | VARCHAR(36) | FK to employee |
| agent_id | VARCHAR(36) | FK to agent |
| assignment_role | VARCHAR(50) | owner/supervisor/sponsor |

---

## Goals

Schema tables: `agent_goal`, `goal_success_criteria`, `goal_constraint`, `timeline`, `timeline_milestone`, `timeline_deadline`

### Goal Definition
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| agent_id | VARCHAR(36) | FK to agent |
| goal_type | VARCHAR(50) | short_term/long_term/ambition |
| description | TEXT | Goal description |
| target_date | DATE | Target completion date |

### Success Criteria
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| goal_id | VARCHAR(36) | FK to agent_goal |
| criteria_type | VARCHAR(50) | Type of criteria |
| criteria_value | TEXT | Criteria value |
| weight | NUMERIC | Weight factor |

### Constraints
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| goal_id | VARCHAR(36) | FK to agent_goal |
| constraint_type | VARCHAR(50) | Type of constraint |
| constraint_value | TEXT | Constraint value |

### Timelines
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| agent_id | VARCHAR(36) | FK to agent |
| name | VARCHAR(255) | Timeline name |
| start_date | DATE | Start date |
| end_date | DATE | End date |
| status | VARCHAR(50) | active/completed/cancelled |

---

## Skills

Schema tables: `agent_skill`, `sfia_skill_master`, `skill_profile`, `skill_profile_skill`

### Agent Skill
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| agent_id | VARCHAR(36) | FK to agent |
| skill_code | VARCHAR(50) | SFIA skill code |
| skill_name | VARCHAR(255) | Skill name |
| proficiency_level | VARCHAR(20) | Level (1-7) |

### Skill Profile Assignment
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| profile_id | VARCHAR(36) | FK to skill_profile |
| skill_code | VARCHAR(50) | FK to sfia_skill_master |
| proficiency_level | VARCHAR(20) | Proficiency |
| is_core | BOOLEAN | Core skill flag |

---

## Credentials / Growth

Schema tables: `employee_certification`, `employee_education` (agent shares certs via relationship or separate table)

> Note: Credentials/growth for agents may need new table: `agent_certification` or `agent_assessment`

**Potential Schema Gap:**
- `agent_assessment` - Agent capability assessments
- `agent_milestone` - Agent progression milestones

---

## Behavior

Schema tables: `agent_profile`

### Profile
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| agent_id | VARCHAR(36) | FK to agent |
| behavioral_profile | JSONB | Personality/preferences |
| operational_profile | JSONB | Working style |

> Note: Consider splitting behavioral/operational into separate columns for clarity

---

## Memory

Schema tables: `agent_memory_profile`

### Memory Configuration
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| agent_id | VARCHAR(36) | FK to agent |
| memory_enabled | BOOLEAN | Enable memory |
| thread_retention_days | INTEGER | Retention period |
| checkpoint_interval_seconds | INTEGER | Checkpoint frequency |

---

## Governance

Schema tables: `agent_governance_profile`

### Governance Profile
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| agent_id | VARCHAR(36) | FK to agent |
| prompt_profile_id | VARCHAR(36) | FK to prompt_profile_master |
| guardrail_profile_id | VARCHAR(36) | FK to guardrail_profile_master |
| approval_profile_id | VARCHAR(36) | FK to approval_profile_master |
| channel_profile_id | VARCHAR(36) | FK to channel_profile_master |

---

## Prompt / Template Assignment

Schema tables: `agent_prompt_assignment`, `prompt_template`

### Prompt Assignment
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| agent_id | VARCHAR(36) | FK to agent |
| prompt_template_id | VARCHAR(36) | FK to prompt_template |
| assigned_at | TIMESTAMP | Assignment time |
| assigned_by | VARCHAR(36) | FK to employee |
| ended_at | TIMESTAMP | End time (null = active) |

---

## Topic Affinities

Schema tables: Not currently modeled

**Potential Schema Gap:**
- `agent_topic_affinity` - Topics agent follows/avoids
  - agent_id
  - topic_code (FK to topic_master)
  - affinity (follows/avoids/neutral)

---

## Sensitive / Private Context

Schema tables: Not currently modeled (by design)

> Note: Sensitive context is intentionally not modeled. If needed:
> - Create separate encrypted table
> - Access-controlled via ownership
> - Not mixed with operational profile

---

## Schema Gaps Found

| Gap | Recommendation |
|-----|--------------|
| agent_assessment | Create table for agent capability assessments |
| agent_milestone | Create table for agent progression milestones |
| agent_topic_affinity | Create table for topic follows/avoids |
| Split behavioral/operational | Consider separate columns in agent_profile |

---

## Sample Agent Profile (JSON)

```json
{
  "id": "agt-coding-assistant-001",
  "tenant_id": "ten-acme-corp",
  "name": "Coding Assistant Alpha",
  "agent_type": "coding_coordinator",
  "is_primary": true,
  
  "identity": {
    "projected_title": "Senior Software Engineer",
    "projected_department": "Engineering",
    "effective_from": "2025-01-01"
  },
  
  "ownership": {
    "owner": "emp-123",
    "supervisor": "emp-456",
    "relationship": "owner"
  },
  
  "goals": [
    {
      "id": "goal-001",
      "type": "short_term",
      "description": "Complete Q2 sprint objectives",
      "target_date": "2025-06-30",
      "success_criteria": ["criteria-001"],
      "constraints": ["constraint-001"]
    }
  ],
  
  "skills": [
    {
      "skill_code": "sfia_PROG",
      "proficiency_level": "5",
      "evidence": "Code review history"
    },
    {
      "skill_code": "sfia_DESI",
      "proficiency_level": "4"
    }
  ],
  
  "governance": {
    "prompt_profile": "prompt_coding_assistant",
    "guardrail_profile": "guardrail_standard",
    "approval_profile": "approval_standard_engineering",
    "channel_profile": "channel_engineering"
  },
  
  "memory": {
    "enabled": true,
    "thread_retention_days": 30,
    "checkpoint_interval_seconds": 60
  },
  
  "behavior": {
    "working_style": "proactive",
    "preferences": {
      "communication_style": "concise",
      "code_style": "typescript"
    }
  }
}
```

---

## Key Design Rules

1. **Agent is not Employee** - Separate IDs, separate tables
2. **One employee → many agents** - Via `employee_agent_assignment`
3. **Primary agent representable** - `is_primary` field on `agent`
4. **Governance via profiles** - External references to profile masters
5. **Sensitive data excluded** - By design, not modeled