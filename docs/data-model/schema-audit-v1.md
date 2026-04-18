# Schema Completeness Audit v1

Audit Date: 2026-04-14
Schema: docs/data-model/schema-v1.sql (73 tables)
Reference: Entity Catalog, ERD v1

---

## Audit Results

| # | Design Requirement | Status | Notes |
|---|-----------------|-------|-------|
| 1 | employee vs agent separation | **PRESENT** | Separate tables: `employee`, `agent` |
| 2 | one employee to many agents | **PRESENT** | `employee_agent_assignment` with role (owner/supervisor/sponsor) |
| 3 | agent-to-agent and agent-to-employee reporting | **PRESENT** | `agent_relationship` with reports_to/delegates_to/supervises/collaborates_with |
| 4 | prompt layer | **PRESENT** | `prompt_profile_master`, `prompt_template`, `prompt_template_version`, `agent_prompt_assignment` |
| 5 | SFIA skill layer | **PRESENT** | `sfia_skill_master`, `skill_profile`, `skill_profile_skill`, `agent_skill` |
| 6 | goal layer | **PRESENT** | `agent_goal`, `goal_success_criteria`, `goal_constraint` |
| 7 | timeline layer | **PRESENT** | `timeline`, `timeline_milestone`, `timeline_deadline`, `timeline_dependency` |
| 8 | product / project / group distinction | **PRESENT** | All three tables exist as separate entities |
| 9 | primary channel for product and group | **PRESENT** | `primary_channel_id` in `product`, `group_entity` |
| 10 | channel roles and permissions | **PRESENT** | `role` in `channel_membership`: owner/moderator/member/viewer |
| 11 | chat and file sharing | **PRESENT** | `channel_message` for chat, `channel_file` for sharing |
| 12 | tasks / deadlines / milestones / reminders / escalations | **PRESENT** | All four tables exist |
| 13 | task comments / attachments / ratings / feedback | **PRESENT** | All four tables exist |
| 14 | human approvals vs rule decisions | **PRESENT** | `approval_request` (human), `decision_record` (rule-based) |
| 15 | overrides | **PRESENT** | `override_record` with override_type |
| 16 | delegation / acting authority / ownership transfer | **PRESENT** | `responsibility_assignment` with assignment_type |
| 17 | certifications / education / employment / growth | **PRESENT** | `employee_certification`, `employee_education`, `employee_employment` |
| 18 | master data IDs for reusable attributes | **PRESENT** | 12 master tables exist |

---

## Detailed Findings

### 1. Employee vs Agent Separation
**Status: PRESENT**
- `employee` table (line 16)
- `agent` table (line 83)
- Modeled as separate entities with different IDs

### 2. One Employee to Many Agents
**Status: PRESENT**
- `employee_agent_assignment` maps employee to agent
- `assignment_role`: owner/supervisor/sponsor
- `is_primary` field on `agent` supports primary agent per employee

### 3. Agent-to-Agent and Agent-to-Employee Reporting
**Status: PRESENT**
- `agent_relationship` table supports:
  - `from_agent_id` → `to_agent_id` (agent reports to agent)
  - `to_employee_id` (agent reports to employee)
  - `relationship_type`: reports_to/delegates_to/supervises/collaborates_with

### 4. Prompt Layer
**Status: PRESENT**
- `prompt_profile_master` - profile container
- `prompt_template` - actual prompt content
- `prompt_template_version` - versioned prompts
- `agent_prompt_assignment` - temporal assignment from employee

### 5. SFIA Skill Layer
**Status: PRESENT**
- `sfia_skill_master` - master list of SFIA skills
- `skill_profile` - named skill profiles
- `skill_profile_skill` - profile-skill associations
- `agent_skill` - agent's SFIA skills

### 6. Goal Layer
**Status: PRESENT**
- `agent_goal` - goal definitions (short-term, long-term, ambitions)
- `goal_success_criteria` - measurable success criteria
- `goal_constraint` - goal constraints

### 7. Timeline Layer
**Status: PRESENT**
- `timeline` - time-bound goal tracking
- `timeline_milestone` - named checkpoints
- `timeline_deadline` - deadlines tied to timeline
- `timeline_dependency` - timeline-to-timeline dependencies

### 8. Product / Project / Group Distinction
**Status: PRESENT**
- `product` - persistent business entity
- `project` - short-term execution
- `group_entity` - community/interest grouping
- All three have distinct IDs and purposes

### 9. Primary Channel for Product and Group
**Status: PRESENT**
- `product.primary_channel_id` references channel
- `group_entity.primary_channel_id` references channel

### 10. Channel Roles and Permissions
**Status: PRESENT**
- `channel_membership.role`: owner/moderator/member/viewer
- Enables permission hierarchy

### 11. Chat and File Sharing
**STATUS: PRESENT**
- `channel_message` - chat messages
- `channel_file` - file sharing via channel

### 12. Tasks / Deadlines / Milestones / Reminders / Escalations
**STATUS: PRESENT**
- `task` - atomic work unit
- `deadline` - task deadlines
- `milestone` / `milestone_task` - progress checkpoints
- `reminder` - reminder entity
- `escalation` - escalation entity

### 13. Task Comments / Attachments / Ratings / Feedback
**STATUS: PRESENT**
- `task_comment` - comments
- `task_attachment` / `task_comment_attachment` - attachments
- `task_rating` - ratings (quality/speed/usefulness/clarity)
- `task_feedback` - written feedback

### 14. Human Approvals vs Rule Decisions
**STATUS: PRESENT**
- `approval_request` - human approval workflow (pending/approved/denied)
- `decision_record` - rule-based decisions (approved_by_rule/rejected_by_rule/etc.)

### 15. Overrides
**STATUS: PRESENT**
- `override_record` - force backend/bypass approval/allow exception

### 16. Delegation / Acting Authority / Ownership Transfer
**STATUS: PRESENT**
- `responsibility_assignment` with:
  - `assignment_type`: delegation/acting_authority/ownership_transfer
  - `from_type`/`from_id` → `to_type`/`to_id`
  - `effective_from`/`effective_to` temporal bounds

### 17. Certifications / Education / Employment / Growth
**STATUS: PRESENT**
- `employee_certification` - credential records
- `employee_education` - education history
- `employee_employment` - employment history
- Separate from SFIA skills

### 18. Master Data IDs
**STATUS: PRESENT**
- `department_master`
- `job_title_master`
- `seniority_level_master`
- `certification_master`
- `institution_master`
- `qualification_type_master`
- `topic_master`
- `sfia_skill_master`
- plus profile masters for prompt/guardrail/approval/channel

---

## Minor Observations (Not Gaps)

| Item | Status | Note |
|------|-------|------|
| `employee_group_membership` | NOT SEPARATE TABLE | Modeled via `group_membership` with `member_type='employee'` |
| `project.channel_id` | PRESENT | Optional channel per project |
| `task_assignment_history` | PRESENT | Audit trail for task ownership |
| `execution_history` | PRESENT | Audit for execution lifecycle |
| `memory_checkpoint` | PRESENT | Checkpoints to memory-service |

---

## Gap Report Summary

**TOTAL: 18/18 requirements covered**
- PRESENT: 18
- PARTIALLY MODELED: 0
- MISSING: 0

---

## Recommendations

No schema gaps found. All design requirements from the entity catalog are explicitly modeled.

Optional enhancements (not gaps):
1. Consider adding `employee_group_membership` as explicit table for clarity (currently via `group_membership`)
2. Add `project.primary_channel_id` for consistency with product/group (currently has `channel_id`)

---

_End of Audit_