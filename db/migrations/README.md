# Autonomyx Database Migrations

This directory contains ordered SQL migration files that build the complete Autonomyx data model.

## Migration Order

| # | File | Tables | Purpose | Dependencies |
|---|------|--------|---------|--------------|
| 001 | `001_master_data.sql` | 12 | Reference/lookup tables | None |
| 002 | `002_tenant_and_employee.sql` | 7 | Core org: tenant, employee, identity | 001 |
| 003 | `003_agent_layer.sql` | 9 | AI agents and relationships | 002 |
| 004 | `004_prompt_skills_goals_timelines.sql` | 14 | Prompt, skills, goals, timelines | 001, 002, 003 |
| 005 | `005_product_project_group.sql` | 4 | Collaboration containers | 002, 003 |
| 006 | `006_workflow.sql` | 16 | Task management | 002, 003, 004, 005 |
| 007 | `007_channels_and_files.sql` | 5 | Communication, files | 002, 003, 004 |
| 008 | `008_tenant_policy.sql` | 3 | Tenant policy and control | 002, 007 |

**Total: 8 migrations, ~73 tables**

## Design Principles

1. **Dependency Order**: Each migration only depends on previously applied migrations
2. **FK Validation**: All foreign key references point to tables created in earlier migrations
3. **Stable IDs**: All primary keys use VARCHAR(36) for UUID consistency
4. **Audit Fields**: All tables include `created_at` and `updated_at` timestamps where appropriate
5. **No Data Loss**: Migration files are additive - no DROP statements

## How to Apply

### Manual Application
```bash
psql -h localhost -U autonomyx -d autonomyx -f 001_master_data.sql
psql -h localhost -U autonomyx -d autonomyx -f 002_tenant_and_employee.sql
# ... continue for each migration
```

### Using a Migration Tool
```bash
flyway migrate
# or
migrate -path db/migrations -database postgres://user:pass@localhost:5432/autonomyx up
```

## Migration to ERD Mapping

```
erd-v1.mmd
│
├── Master Data (Section 8)
│   └── → 001_master_data.sql
│       - department_master, job_title_master, seniority_level_master
│       - sfia_skill_master, certification_master, institution_master
│       - prompt_profile_master, guardrail_profile_master
│       - approval_profile_master, channel_profile_master
│
├── Core Organization (Section 1)
│   └── → 002_tenant_and_employee.sql
│       - tenant, employee, employee_identity
│       - employee_employment, employee_education, employee_certification
│
├── Agent Layer (Section 2)
│   └── → 003_agent_layer.sql
│       - agent, agent_identity, agent_profile
│       - agent_skill, agent_governance_profile, agent_memory_profile
│       - employee_agent_assignment, agent_relationship
│
├── Prompt / Skills / Goals / Timelines (Section 2)
│   └── → 004_prompt_skills_goals_timelines.sql
│       - prompt_template, prompt_template_version, agent_prompt_assignment
│       - skill_profile, skill_profile_skill
│       - agent_goal, goal_success_criteria, goal_constraint
│       - timeline, timeline_milestone, timeline_deadline, timeline_dependency
│       - agent_group_membership
│
├── Collaboration Containers (Section 3)
│   └── → 005_product_project_group.sql
│       - product, project, group_entity, group_membership
│
├── Workflow Entities (Sections 4-5)
│   └── → 006_workflow.sql
│       - task, task_dependency, task_assignment_history
│       - deadline, milestone, milestone_task
│       - reminder, escalation
│       - task_comment, task_attachment, task_rating, task_feedback
│
├── Channels and Files (Section 6)
│   └── → 007_channels_and_files.sql
│       - channel, channel_membership, channel_message
│       - file_asset, channel_file
│
└── Decision and Control Plane (Section 7)
    └── → 007_decision_control_plane.sql + 008_tenant_policy.sql
        - execution_request, execution_request_metadata
        - policy_resolution, backend_selection, fallback_event
        - approval_request, decision_record, override_record
        - responsibility_assignment, usage_record
        - memory_checkpoint, execution_history
        - tenant_policy, tenant_policy_backend_rule, tenant_capability_policy
```

## Adding New Migrations

When adding new entities:
1. Create a new migration file with next sequential number
2. Add header comment describing purpose, tables, ERD mapping, dependencies
3. Ensure all FK references point to tables in earlier migrations
4. Add any necessary indexes at the end of the migration
5. Update this README with the new migration info

## Rollback Strategy

These migrations are designed to be idempotent for initial setup. For production:
- Use a migration tool that supports down migrations
- Never modify applied migrations - create new ones for changes
- Test migrations in a non-production environment first