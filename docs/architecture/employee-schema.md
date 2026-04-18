# Employee Schema

This document defines the complete employee domain model, keeping employee and agent as separate entities.

---

## Employee vs Agent Separation

**Core Rule**: Employee (human) and Agent (AI) are **separate** entities with different IDs.

| Entity | Table | Description |
|--------|-------|-------------|
| Human | `employee` | Real-world person |
| AI | `agent` | AI agent entity |

---

## Identity / Org Context

Schema tables: `employee`, `employee_identity`

### Core Employee
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key (UUID) |
| tenant_id | VARCHAR(36) | FK to tenant |
| email | VARCHAR(255) | Unique email |
| name | VARCHAR(255) | Full name |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

### Current Identity
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| employee_id | VARCHAR(36) | FK to employee |
| job_title | VARCHAR(255) | Current job title (FK recommended) |
| department | VARCHAR(255) | Current department (FK recommended) |
| seniority | VARCHAR(50) | Seniority level (FK recommended) |
| reporting_to_employee_id | VARCHAR(36) | FK to manager |
| effective_from | TIMESTAMP | Effective from |
| effective_to | TIMESTAMP | Effective to |

---

## Real-World Records

### Employment History
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| employee_id | VARCHAR(36) | FK to employee |
| start_date | DATE | Employment start |
| end_date | DATE | Employment end |
| employment_type | VARCHAR(50) | Full-time/part-time/contract |

### Education
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| employee_id | VARCHAR(36) | FK to employee |
| institution | VARCHAR(255) | Institution name |
| degree | VARCHAR(255) | Degree earned |
| field_of_study | VARCHAR(255) | Major/minor |
| start_date | DATE | Start date |
| end_date | DATE | End date |

### Certifications
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| employee_id | VARCHAR(36) | FK to employee |
| certification_code | VARCHAR(50) | Code (FK recommended) |
| certification_name | VARCHAR(255) | Name |
| issued_date | DATE | Date issued |
| expiry_date | DATE | Expiration date |

---

## Group Memberships

Schema table: `group_membership`

| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| group_id | VARCHAR(36) | FK to group_entity |
| member_type | VARCHAR(20) | employee/agent/group |
| member_id | VARCHAR(36) | FK to member |
| joined_at | TIMESTAMP | Join timestamp |

---

## Relationship to Agents

Schema table: `employee_agent_assignment`

### Ownership / Supervision
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| employee_id | VARCHAR(36) | FK to employee |
| agent_id | VARCHAR(36) | FK to agent |
| assignment_role | VARCHAR(50) | owner/supervisor/sponsor |
| assigned_at | TIMESTAMP | Assignment time |
| ended_at | TIMESTAMP | End time |

---

## Example Scenarios

### Scenario 1: One Employee Owning Multiple Agents

```
Employee: emp-123 (Alice)
├── Agent: agt-coding-001 (Primary coding agent) - role: owner
├── Agent: agt-analysis-001 (Data analysis agent) - role: owner
└── Agent: agt-research-001 (Research agent) - role: owner
```

### Scenario 2: Employee Supervising Another Employee's Agent

```
Employee: emp-456 (Bob - Manager)
└── Agent: agt-coding-001 - role: supervisor (for emp-123's agent)

Employee: emp-123 (Alice - Individual contributor)
└── Agent: agt-coding-001 - role: owner
```

### Scenario 3: Delegation Through Agent Network

```
Employee A (emp-123) delegates to Employee B (emp-789):
- Via agent_relationship: agt-coding-001 (owned by A) delegates to emp-789
- Or via responsibility_assignment for specific tasks
```

---

## Sample Employee Profile (JSON)

```json
{
  "id": "emp-123",
  "tenant_id": "ten-acme-corp",
  "email": "alice@acme.com",
  "name": "Alice Chen",
  
  "current_identity": {
    "job_title": "job_title_senior_software_engineer",
    "department": "dept_engineering",
    "seniority": "sen_l4_principal",
    "reporting_to": "emp-456",
    "effective_from": "2024-01-15"
  },
  
  "employment_history": [
    {
      "start_date": "2022-03-01",
      "end_date": null,
      "employment_type": "full_time"
    }
  ],
  
  "education": [
    {
      "institution": "inst_stanford",
      "degree": "BS Computer Science",
      "field_of_study": "cs",
      "end_date": "2022"
    }
  ],
  
  "certifications": [
    {
      "certification_code": "cert_aws_sa_pro",
      "issued_date": "2023-06-01"
    }
  ],
  
  "group_memberships": [
    {"group_id": "grp-eng-guild", "role": "member"},
    {"group_id": "grp-ai-interest", "role": "member"}
  ],
  
  "agent_relationships": [
    {
      "agent_id": "agt-coding-001",
      "role": "owner",
      "since": "2024-01-01"
    },
    {
      "agent_id": "agt-analysis-001", 
      "role": "owner",
      "since": "2024-03-15"
    }
  ]
}
```

---

## Schema Gaps Found

| Gap | Recommendation |
|-----|---------------|
| None identified | Current schema covers employee domain |

---

## Key Design Rules

1. **Employee ≠ Agent** - Separate tables, separate IDs
2. **One employee → many agents** - Via `employee_agent_assignment`
3. **Real-world data on employee** - Employment, education, certs stay on employee
4. **Agent projection** - Agent has `projected_title`, not actual HR data
5. **Group membership unified** - Both employees and agents via `group_membership`