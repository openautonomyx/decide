# Schema v2 Complete - Validation & Mapping Notes

## Overview

This document maps the reconstructed schema v2 against recovered artifacts and flags where fields were reconstructed vs original.

## Files

- **schema-v2-complete.sql** - Complete PostgreSQL DDL with 76 tables across 12 functional families
- **schema-v1.sql** - Original recovered schema (normalized, foundational)

## Recovery Status Legend

| Flag | Meaning |
|------|--------|
| [O] | Original - recovered from schema-v1.sql or other artifacts |
| [R] | Reconstructed - inferred from architecture to complete schema |

## Table Mapping Summary

| # | Table Name | Source | Notes |
|---|-----------|-------|-------|
| 1 | master_country | [O] | ISO country codes |
| 2 | master_region | [O] | Country/region hierarchy |
| 3 | master_department | [O] | Org structure |
| 4 | master_job_title | [O] | Job families & levels |
| 5 | master_skill | [O] | SFIA framework aligned |
| 6 | master_certification | [O] | Credential tracking |
| 7 | master_topic | [O] | Knowledge domains |
| 8 | master_channel | [O] | Communication channels |
| 9 | master_policy_type | [O] | Policy type registry |
| 10 | master_memory_profile_template | [O] | 9-layer memory defaults |
| 11 | tenant | [O] | Core tenant entity |
| 12 | tenant_settings | [R] | Tenant configuration |
| 13 | partner_account | [R] | Partner tracking |
| 14 | partner_account_sponsor | [R] | Partner relationships |
| 15 | organization_membership | [R] | Identity-org links |
| 16 | identity | [O] | Unified identity |
| 17 | identity_attribute | [O] | Flexible attributes |
| 18 | identity_lifecycle_state | [R] | State transitions |
| 19 | identity_auth_projection | [R] | IAM projection |
| 20 | employee | [O] | Human employee |
| 21 | employee_profile | [O] | PII, preferences |
| 22 | employee_skill | [O] | Skill mapping |
| 23 | employee_certification | [O] | Credentials |
| 24 | employee_education | [O] | Academic history |
| 25 | employee_employment_history | [O] | Work history |
| 26 | employee_group_membership | [O] | Group affiliations |
| 27 | agent | [O] | AI agent |
| 28 | agent_profile | [O] | Persona, prompts |
| 29 | agent_goal | [O] | Goal tracking |
| 30 | agent_skill_profile | [O] | Agent capabilities |
| 31 | agent_preference | [O] | Runtime prefs |
| 32 | agent_constraint | [O] | Guardrails |
| 33 | agent_memory_profile | [O] | 9-layer config |
| 34 | agent_governance_profile | [O] | Approval limits |
| 35 | agent_group_membership | [O] | Group membership |
| 36 | agent_identity_credential_ref | [R] | Credential refs |
| 37 | employee_agent_assignment | [O] | Human-agent link |
| 38 | employee_agent_supervision | [R] | Oversight link |
| 39 | employee_agent_goal_link | [R] | Goal ownership |
| 40 | employee_agent_skill_inheritance | [R] | Skill transfer |
| 41 | agent_reporting_line | [R] | Agent hierarchy |
| 42 | product | [O] | Product entity |
| 43 | project | [O] | Project entity |
| 44 | group_entity | [O] | Group/community |
| 45 | product_project_group_link | [R] | Linkage table |
| 46 | task | [O] | Task entity |
| 47 | milestone | [R] | Project milestones |
| 48 | reminder | [O] | Notification scheduling |
| 49 | escalation | [O] | Escalation handling |
| 50 | delegation | [O] | Delegation scope |
| 51 | channel_account | [R] | Channel handles |
| 52 | conversation_thread | [R] | Thread context |
| 53 | message_event | [R] | Message store |
| 54 | file_asset | [O] | File storage |
| 55 | file_link | [O] | File attachment |
| 56 | decision | [O] | Decision record |
| 57 | decision_workspace | [O] | Decision context |
| 58 | decision_alternative | [O] | Options |
| 59 | decision_evidence | [O] | Evidence store |
| 60 | decision_assumption | [O] | Assumptions |
| 61 | decision_constraint | [O] | Constraints |
| 62 | decision_scorecard | [O] | Scoring |
| 63 | decision_outcome_review | [O] | Post-decision |
| 64 | approval | [O] | Approval workflow |
| 65 | approval_step | [R] | Multi-step approval |
| 66 | override_event | [O] | Override tracking |
| 67 | policy_bundle | [O] | Policy bundling |
| 68 | policy_rule | [O] | Policy rules |
| 69 | rbac_role | [O] | RBAC roles |
| 70 | rbac_role_binding | [O] | Role assignment |
| 71 | tool_permission | [O] | Tool access |
| 72 | execution_request | [O] | Execution queue |
| 73 | execution_record | [O] | Run history |
| 74 | memory_record | [O] | 9-layer memory |
| 75 | memory_checkpoint | [O] | State snapshots |
| 76 | audit_event | [O] | Audit trail |

## Architecture Principles Validated

✅ Human employee and agent are never merged
✅ Product, project, and group remain distinct
✅ Workflow entities explicit: task, milestone, reminder, escalation
✅ Decision/control-plane explicit: approval, decision, override, delegation, RBAC, audit
✅ 9-layer memory model preserved
✅ Auth projects to IAM but domain truth stays in tables
✅ JSONB used sparingly

## Next Steps for Validation

1. **Compare against local repo** - Check if any tables/fields differ from actual implementation
2. **Run against test database** - Execute DDL against PostgreSQL to verify syntax
3. **Integrate with Alembic** - Convert to migration scripts if needed
4. **Add data migration scripts** - Populate master data

## Notes Removed from Schema

The following were intentionally excluded to keep DDL clean:

- Application logic (triggers, stored procedures)
- Seed data (separate files)
- Full-text search indexes (optional)
- Partitioning strategies (tenant-specific)

## Delta Summary

The delta-v1 appendix adds:

| Category | New Tables | Updated Tables |
|----------|-----------|----------------|
| Content-type review | 6 master + 6 operational | 0 |
| Workflow templates | 5 | 0 |
| ITSM/CMDB | 6 | 0 |
| Enterprise processes | 3 | 0 |
| Hiring workflow | 4 | 0 |
| Churn reduction | 3 | 0 |
| **Subtotals** | **31 new** | **7 updated** |

### Updated Tables (from delta U1-U8)

- `approval` - +content_item_id, workflow_instance_id, process_case_id
- `task` - +workflow_instance_id, process_case_id, action_code, content_item_id
- `decision` - +process_case_id, content_item_id, review_workflow_id
- `file_asset` - +document_type_id, content_item_id, source_template_id
- `message_event` - +action_code, process_case_id
- `partner_account` - +partner_tier, relationship_stage, default_review_template_id
- `master_channel` - +schema_org_type

### Total Tables

| Schema | Tables |
|--------|--------|
| schema-v2-complete.sql | 76 |
| schema-delta-v1.sql (new) | 31 |
| **Total** | **107** |

## Contact for Validation

Schema reconstructed based on:
- docs/data-model/schema-v1.sql
- docs/data-model/master-data-dictionary.md
- Architecture notes from checkpoint
- Delta appendix v1 (this session)