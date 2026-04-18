# Entity Catalog v1

## Purpose

This catalog defines the core entities for the Autonomyx decision-intelligence platform.

It separates:
- human entities
- agent entities
- collaboration containers
- workflow entities
- channel and file-sharing entities
- decision and control-plane entities
- master/reference data

---

## 1. Core Organization

| Entity | Description |
|--------|-------------|
| tenant | Organization or customer boundary |
| employee | Human person inside a tenant |
| employee_identity | Current org identity: title, department, seniority, reporting line |
| employee_employment | Employment history records |
| employee_education | Education records |
| employee_certification | Credential records |
| employee_group_membership | Group membership |

---

## 2. Agent Layer

| Entity | Description |
|--------|-------------|
| agent | AI agent entity; employee may have multiple |
| agent_identity | Operational identity: title, department, reporting |
| agent_profile | Behavioral/operational profile |
| agent_goal | Short-term, long-term goals, ambitions |
| agent_skill | SFIA-based skill records |
| agent_governance_profile | Prompt/guardrail/approval/channel profiles |
| agent_memory_profile | Memory and thread behavior links |
| employee_agent_assignment | owner/supervisor/sponsor relationship |
| agent_relationship | reports_to/delegates_to/supervises/collaborates_with |

---

## 3. Collaboration Containers

| Entity | Description |
|--------|-------------|
| product | Persistent business entity (strategy, roadmap, ownership) |
| project | Short-term execution (timeline, deliverables, milestones) |
| group_entity | Community/interest/committee/guild/hobby grouping |
| group_membership | Employee/agent in group |

---

## 4. Workflow Entities

| Entity | Description |
|--------|-------------|
| task | Atomic unit of work |
| task_dependency | Dependency between tasks |
| task_assignment_history | Audit trail of ownership changes |
| deadline | One or more deadlines on a task |
| milestone | Named progress checkpoint |
| milestone_task | Milestone-task join |
| reminder | Reminder for task/milestone/thread |
| escalation | Missed deadline/blocker/no-response/risk/escalation |

---

## 5. Workflow Collaboration

| Entity | Description |
|--------|-------------|
| task_comment | Comment on task |
| task_comment_attachment | Attachment linked to comment |
| task_attachment | Direct task attachment |
| task_rating | quality/speed/usefulness/clarity rating |
| task_feedback | Written feedback |

---

## 6. Channels and File Sharing

| Entity | Description |
|--------|-------------|
| channel | Conversation surface; contexts: product/project/group/task/direct |
| channel_membership | employee/agent/group in channel |
| channel_message | Chat or system message |
| file_asset | Stored file/binary |
| channel_file | File shared in channel |

---

## 7. Decision and Control Plane

| Entity | Description |
|--------|-------------|
| execution_request | Request entering decision system |
| execution_request_metadata | tenant_id/user_id/user_license/task_risk/budget_tier |
| policy_resolution | Resolved policy output |
| backend_selection | Selected backend + routing reason |
| fallback_event | Fallback from one backend to another |
| approval_request | Human approval request (vs rule-based) |
| decision_record | approved/rejected/awaiting/approved_by_human/rejected_by_human |
| override_record | Force backend/bypass approval/allow exception |
| responsibility_assignment | Delegation/acting authority/ownership transfer |
| usage_record | Normalized usage/cost/latency |
| memory_checkpoint | Checkpoint to memory-service |
| execution_history | Audit trail of execution |

---

## 8. Master Data

| Entity | Description |
|--------|-------------|
| department_master | Departments |
| job_title_master | Job titles |
| seniority_level_master | Seniority levels |
| sfia_skill_master | SFIA skills |
| certification_master | Certifications |
| institution_master | Institutions |
| qualification_type_master | Qualification types |
| topic_master | Topics |
| prompt_profile_master | Prompt profiles |
| guardrail_profile_master | Guardrail profiles |
| approval_profile_master | Approval profiles |
| channel_profile_master | Channel profiles |

---

## 9. Modeling Rules

1. Human and agent are separate entities
2. One employee may have multiple agents
3. One primary human-facing agent per employee is the preferred default
4. Agents may report to other agents or to employees
5. Product, project, and group are different containers - must not be merged
6. Task, deadline, milestone, reminder, escalation are first-class workflow entities
7. Approval and rule-based decisions are different entity types
8. Override is first-class
9. Product and group should each have one primary channel
10. Channels support chat and file sharing