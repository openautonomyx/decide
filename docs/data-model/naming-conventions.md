# Naming Conventions v1

This document defines ID and naming conventions for the Autonomyx platform to ensure consistency across APIs, UIs, and databases.

---

## ID Format Conventions

All stable IDs use the format: `<prefix>_<snake_case_description>`

| ID Family | Prefix | Format | Example |
|----------|--------|--------|---------|
| Department | `dept_` | `dept_<snake>` | `dept_brand_creative` |
| Job Title | `job_title_` | `job_title_<snake>` | `job_title_senior_design_strategist` |
| Seniority | `sen_` | `sen_<level>` | `sen_l4_principal` |
| SFIA Skill | `sfia_` | `sfia_<CODE>` | `sfia_PROG` |
| Certification | `cert_` | `cert_<snake>` | `cert_aws_sa_pro` |
| Institution | `inst_` | `inst_<snake>` | `inst_stanford` |
| Qualification | `qualf_` | `qualf_<snake>` | `qualf_bs_cs` |
| Topic | `topic_` | `topic_<snake>` | `topic_ml_ops` |
| Group | `group_` | `group_<snake>` | `group_design_guild` |
| Approval Profile | `approval_` | `approval_<snake>` | `approval_standard_engineering` |
| Guardrail Profile | `guardrail_` | `guardrail_<snake>` | `guardrail_strict` |
| Prompt Profile | `prompt_` | `prompt_<snake>` | `prompt_coding_assistant` |
| Channel Profile | `channel_` | `channel_<snake>` | `channel_restricted` |

---

## Table Naming Conventions

| Entity Type | Naming | Example |
|------------|--------|---------|
| Master/Reference | `<entity>_master` | `department_master` |
| Identity | `<entity>_identity` | `employee_identity` |
| Profile | `<entity>_profile` | `agent_profile` |
| Assignment | `<entity>_<entity>_assignment` | `employee_agent_assignment` |
| Membership | `<entity>_membership` | `group_membership` |
| Relationship | `<entity>_relationship` | `agent_relationship` |
| Dependency | `<entity>_dependency` | `task_dependency` |
| Attachment | `<entity>_attachment` | `task_attachment` |
| Comment | `<entity>_comment` | `task_comment` |
| History | `<entity>_history` | `task_assignment_history` |

---

## Foreign Key Naming Conventions

| From Table | To Table | FK Name |
|-----------|---------|--------|
| employee | tenant | `tenant_id` |
| employee | employee | `reporting_to_employee_id` |
| agent | tenant | `tenant_id` |
| agent | employee | (via employee_agent_assignment) |
| task | project | `project_id` |
| task | employee | `assigned_to_employee_id` |
| task | agent | `assigned_to_agent_id` |
| channel | tenant | `tenant_id` |
| execution_request | tenant | `tenant_id` |

---

## Enum/Status Naming Conventions

### task.status
```
pending → Task created, not started
in_progress → Task actively being worked
completed → Task finished
blocked → Task blocked by dependency
cancelled → Task cancelled
```

### approval_request.status
```
pending → Awaiting human decision
approved → Approved by approver
denied → Denied by approver
expired → Approval request expired
```

### decision_record.decision_type
```
approved_by_rule → Auto-approved by policy
rejected_by_rule → Auto-rejected by policy
awaiting_human → Needs human approval
approved_by_human → Human approved
rejected_by_human → Human rejected
```

### override_record.override_type
```
force_backend → Force specific backend
bypass_approval → Skip approval check
allow_exception → Allow normally denied
change_deadline → Modify deadline
change_goal → Modify goal
```

### responsibility_assignment.assignment_type
```
delegation → Temporary authority transfer
acting_authority → Acting in another role
ownership_transfer → Permanent ownership change
```

### escalation.escalation_type
```
missed_deadline → Deadline missed
blocker → Task blocked
no_response → No response from assignee
risk_increase → Risk level increased
manual → Manual escalation
```

### reminder.reminder_type
```
deadline → Deadline reminder
checkin → Check-in reminder
followup → Follow-up reminder
approval → Approval reminder
```

### channel_membership.role
```
owner → Full control
moderator → Manage messages/members
member → Standard access
viewer → Read-only access
```

---

## Audit Field Naming Conventions

All tables MUST include these fields where applicable:

| Field | Type | Purpose |
|-------|------|---------|
| `created_at` | TIMESTAMP | Record creation time |
| `updated_at` | TIMESTAMP | Last modification time |
| `created_by` | VARCHAR(36) | FK to employee who created |
| `updated_by` | VARCHAR(36) | FK to employee who modified |

Temporal fields use suffix:
- `_at` for timestamps (e.g., `created_at`)
- `_date` for date-only (e.g., `start_date`)
- `effective_from` / `effective_to` for date ranges

---

## JSON/JSONB Field Conventions

Use JSONB only when flexibility is genuinely needed:

| Field | Type | Used In |
|------|-------|--------|
| `effective_policy` | policy_resolution |
| `fallback_order` | backend_selection |
| `rules` | *_profile_master tables |
| `settings` | channel_profile_master |
| `event_data` | execution_history |
| `checkpoint_data` | memory_checkpoint |
| `approval_required_for` | tenant_policy |
| `behavioral_profile` | agent_profile |
| `operational_profile` | agent_profile |

---

## Master Data vs Transactional Tables

### Must Use Master Data
- `employee_identity.job_title` → FK to `job_title_master.code`
- `employee_identity.department` → FK to `department_master.code`
- `employee_identity.seniority` → FK to `seniority_level_master.code`
- `agent_skill.skill_code` → FK to `sfia_skill_master.code`

### Should Be Transactional
- `task.status` → Direct enum (not master)
- `approval_request.status` → Direct enum (not master)
- `channel.role` → Direct enum (not master)

### Can Be Either (Case-by-Case)
- `group_entity.group_type` → Can be master or transactional
- `task.priority` → Can be master or transactional

---

## Examples

### Complete ID Chains

```
Employee → dept_brand_creative → job_title_senior_design_strategist → sen_l4_principal
Agent → agent_coding_assistant_001 → prompt_coding_assistant → sfia_PROG
Task → task_proj_ml_launch_001 → deadline_q2_review → milestone_launch
```

### FK References

```sql
-- Correct
INSERT INTO employee_identity (employee_id, job_title) 
VALUES ('emp-123', 'job_title_senior_design_strategist');

-- Incorrect - don't use free text
INSERT INTO employee_identity (employee_id, job_title) 
VALUES ('emp-123', 'Senior Design Strategist');
```

---

## Anti-Patterns to Avoid

1. **Don't use free text for master-curated fields**
   - ✗ `job_title = 'Senior Designer'`
   - ✓ `job_title = 'job_title_senior_designer'`

2. **Don't mix ID formats**
   - ✗ `dept_creative` in one table, `dept_brand_creative` in another
   - ✓ Use consistent prefix across all tables

3. **Don't create new master codes without following convention**
   - ✗ New code: `D1`
   - ✓ New code: `dept_new_capability`

4. **Don't use auto-increment for entity IDs**
   - ✗ `id = 1, 2, 3`
   - ✓ `id = 'uuid-or-generated-id'`

---

_End of Naming Conventions_