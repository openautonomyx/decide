# Master Data Dictionary v1

This document defines all master/reference data tables in the Autonomyx platform with ID conventions.

---

## ID Format Conventions

| ID Family | Format | Example | Used By |
|----------|-------|--------|---------|
| Department | `dept_<snake>` | `dept_brand_creative` | `department_master.code` |
| Job Title | `job_title_<snake>` | `job_title_senior_design_strategist` | `job_title_master.code` |
| Seniority | `sen_<snake>` | `sen_l4_principal` | `seniority_level_master.code` |
| SFIA Skill | `sfia_<code>` | `sfia_PROG` | `sfia_skill_master.code` |
| Certification | `cert_<snake>` | `cert_aws_sa_pro` | `certification_master.code` |
| Institution | `inst_<snake>` | `inst_stanford` | `institution_master.code` |
| Qualification | `qualf_<snake>` | `qualf_bs_cs` | `qualification_type_master.code` |
| Topic | `topic_<snake>` | `topic_ml_ops` | `topic_master.code` |
| Group | `group_<snake>` | `group_design_guild` | `group_entity.group_type` + name |
| Approval Profile | `approval_<snake>` | `approval_standard_engineering` | `approval_profile_master.name` |
| Guardrail Profile | `guardrail_<snake>` | `guardrail_strict` | `guardrail_profile_master.name` |
| Prompt Profile | `prompt_<snake>` | `prompt_coding_assistant` | `prompt_profile_master.name` |
| Channel Profile | `channel_<snake>` | `channel_restricted` | `channel_profile_master.name` |

---

## Core Organization

### tenant
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key (UUID) |
| name | VARCHAR(255) | Tenant/organization name |
| enabled | BOOLEAN | Whether tenant is active |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

### employee
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key (UUID) |
| tenant_id | VARCHAR(36) | FK to tenant |
| email | VARCHAR(255) | Unique email address |
| name | VARCHAR(255) | Full name |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

### employee_identity
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key (UUID) |
| employee_id | VARCHAR(36) | FK to employee |
| job_title | VARCHAR(255) | Job title (FK to job_title_master.code recommended) |
| department | VARCHAR(255) | Department (FK to department_master.code recommended) |
| seniority | VARCHAR(50) | Seniority level (FK to seniority_level_master.code recommended) |
| reporting_to_employee_id | VARCHAR(36) | FK to reporting employee |
| effective_from | TIMESTAMP | Identity effective from date |
| effective_to | TIMESTAMP | Identity effective to date |

---

## Agent Layer

### agent
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key (UUID) |
| tenant_id | VARCHAR(36) | FK to tenant |
| name | VARCHAR(255) | Agent name |
| agent_type | VARCHAR(50) | Type of agent |
| is_primary | BOOLEAN | Primary human-facing agent |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

### employee_agent_assignment
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key (UUID) |
| employee_id | VARCHAR(36) | FK to employee |
| agent_id | VARCHAR(36) | FK to agent |
| assignment_role | VARCHAR(50) | owner/supervisor/sponsor |
| assigned_at | TIMESTAMP | Assignment timestamp |
| ended_at | TIMESTAMP | Assignment end timestamp |

---

## Collaboration Containers

### product
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key (UUID) |
| tenant_id | VARCHAR(36) | FK to tenant |
| name | VARCHAR(255) | Product name |
| strategy | TEXT | Product strategy |
| primary_channel_id | VARCHAR(36) | FK to primary channel |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

### project
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key (UUID) |
| tenant_id | VARCHAR(36) | FK to tenant |
| name | VARCHAR(255) | Project name |
| start_date | DATE | Project start |
| end_date | DATE | Project end |
| channel_id | VARCHAR(36) | Optional channel |

### group_entity
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key (UUID) |
| tenant_id | VARCHAR(36) | FK to tenant |
| name | VARCHAR(255) | Group name |
| group_type | VARCHAR(50) | community/interest/committee/guild |
| primary_channel_id | VARCHAR(36) | FK to primary channel |

---

## Workflow

### task
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key (UUID) |
| tenant_id | VARCHAR(36) | FK to tenant |
| project_id | VARCHAR(36) | FK to project |
| title | VARCHAR(255) | Task title |
| description | TEXT | Task description |
| status | VARCHAR(50) | pending/in_progress/completed/blocked |
| priority | VARCHAR(20) | low/medium/high/urgent |
| assigned_to_employee_id | VARCHAR(36) | FK to employee |
| assigned_to_agent_id | VARCHAR(36) | FK to agent |

### milestone
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key (UUID) |
| project_id | VARCHAR(36) | FK to project |
| name | VARCHAR(255) | Milestone name |
| target_date | DATE | Target completion date |

---

## Channels

### channel
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key (UUID) |
| tenant_id | VARCHAR(36) | FK to tenant |
| context_type | VARCHAR(50) | product/project/group/task/direct |
| context_id | VARCHAR(36) | FK to context entity |
| name | VARCHAR(255) | Channel name |
| is_primary | BOOLEAN | Primary channel for container |

### channel_membership
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key (UUID) |
| channel_id | VARCHAR(36) | FK to channel |
| member_type | VARCHAR(20) | employee/agent/group |
| member_id | VARCHAR(36) | FK to member |
| role | VARCHAR(50) | owner/moderator/member/viewer |

---

## Decision & Control Plane

### execution_request
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key (UUID) |
| tenant_id | VARCHAR(36) | FK to tenant |
| goal | TEXT | Goal/description |
| capability | VARCHAR(50) | coding/image_editing/etc |
| quality | VARCHAR(50) | basic/standard/premium |
| status | VARCHAR(50) | pending/running/success/error |
| created_at | TIMESTAMP | Request timestamp |
| completed_at | TIMESTAMP | Completion timestamp |

### execution_request_metadata
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key (UUID) |
| execution_request_id | VARCHAR(36) | FK to execution_request |
| key | VARCHAR(100) | Metadata key |
| value | TEXT | Metadata value |

### approval_request
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key (UUID) |
| execution_request_id | VARCHAR(36) | FK to execution_request |
| status | VARCHAR(50) | pending/approved/denied |
| requested_by_type | VARCHAR(20) | employee/system |
| requested_by_id | VARCHAR(36) | FK to requester |
| approver | VARCHAR(36) | FK to employee |
| approver_notes | TEXT | Approval notes |
| requested_at | TIMESTAMP | Request timestamp |
| decided_at | TIMESTAMP | Decision timestamp |

### usage_record
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key (UUID) |
| execution_request_id | VARCHAR(36) | FK to execution_request |
| backend_used | VARCHAR(50) | Backend identifier |
| provider | VARCHAR(50) | LLM provider |
| model | VARCHAR(100) | Model name |
| input_tokens | INTEGER | Input token count |
| output_tokens | INTEGER | Output token count |
| total_tokens | INTEGER | Total tokens |
| cost | NUMERIC(10,6) | Cost in USD |
| latency_ms | INTEGER | Latency in milliseconds |

### execution_history
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key (UUID) |
| execution_request_id | VARCHAR(36) | FK to execution_request |
| thread_id | VARCHAR(36) | Thread identifier |
| event_type | VARCHAR(50) | Event type |
| event_data | JSONB | Event payload |
| created_at | TIMESTAMP | Event timestamp |

---

## Master Reference Tables

### department_master
| Field | Type | Description |
|-------|------|-------------|
| code | VARCHAR(20) | Primary key (e.g., `dept_brand_creative`) |
| name | VARCHAR(255) | Department name |
| parent_department_code | VARCHAR(20) | Parent department |

### job_title_master
| Field | Type | Description |
|-------|------|-------------|
| code | VARCHAR(20) | Primary key (e.g., `job_title_senior_design_strategist`) |
| name | VARCHAR(255) | Job title name |

### seniority_level_master
| Field | Type | Description |
|-------|------|-------------|
| code | VARCHAR(20) | Primary key (e.g., `sen_l4_principal`) |
| name | VARCHAR(255) | Seniority name |
| level_order | INTEGER | Sort order |

### sfia_skill_master
| Field | Type | Description |
|-------|------|-------------|
| code | VARCHAR(20) | Primary key (e.g., `sfia_PROG`) |
| name | VARCHAR(255) | Skill name |
| category | VARCHAR(100) | SFIA category |

### prompt_profile_master
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| name | VARCHAR(255) | Profile name (e.g., `prompt_coding_assistant`) |
| description | TEXT | Profile description |
| is_default | BOOLEAN | Default profile flag |

### guardrail_profile_master
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| name | VARCHAR(255) | Profile name (e.g., `guardrail_strict`) |
| rules | JSONB | Guardrail rules |

### approval_profile_master
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| name | VARCHAR(255) | Profile name (e.g., `approval_standard_engineering`) |
| rules | JSONB | Approval rules |

### channel_profile_master
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(36) | Primary key |
| name | VARCHAR(255) | Profile name |
| settings | JSONB | Channel settings |