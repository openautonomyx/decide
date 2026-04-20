# Decide Data Models Knowledge Pack

Use this file in Langflow Knowledge/RAG to ground flows on Decide model names and fields.

## AgentBase
Source: `app/schemas/agent.py`

- name
- agent_type
- is_primary

## AgentCreate
Source: `app/schemas/agent.py`

- tenant_id

## AgentUpdate
Source: `app/schemas/agent.py`

- name
- agent_type
- is_primary

## Agent
Source: `app/schemas/agent.py`

- id
- tenant_id
- created_at
- updated_at

## AgentWithRelations
Source: `app/schemas/agent.py`

- owner_employee_id
- goals
- skills

## AgentGoalBase
Source: `app/schemas/agent.py`

- goal_type
- description
- target_date

## AgentGoalCreate
Source: `app/schemas/agent.py`

- agent_id

## AgentGoal
Source: `app/schemas/agent.py`

- id
- agent_id
- created_at

## AgentSkillBase
Source: `app/schemas/agent.py`

- skill_code
- skill_name
- proficiency_level

## AgentSkillCreate
Source: `app/schemas/agent.py`

- agent_id

## AgentSkill
Source: `app/schemas/agent.py`

- id
- agent_id

## EmployeeAgentAssignmentBase
Source: `app/schemas/agent.py`

- assignment_role

## EmployeeAgentAssignmentCreate
Source: `app/schemas/agent.py`

- employee_id
- agent_id

## EmployeeAgentAssignment
Source: `app/schemas/agent.py`

- id
- employee_id
- agent_id
- assigned_at
- ended_at

## AgentList
Source: `app/schemas/agent.py`

- total
- items

## TenantBase
Source: `app/schemas/tenant.py`

- name
- enabled

## TenantCreate
Source: `app/schemas/tenant.py`

- (no parsed fields)

## TenantUpdate
Source: `app/schemas/tenant.py`

- name
- enabled

## Tenant
Source: `app/schemas/tenant.py`

- id
- created_at
- updated_at

## TenantList
Source: `app/schemas/tenant.py`

- total
- items

## TraceSessionBase
Source: `app/schemas/trace.py`

- tenant_id
- trace_id
- session_type
- status
- duration_ms
- metadata

## TraceSessionCreate
Source: `app/schemas/trace.py`

- (no parsed fields)

## TraceSessionUpdate
Source: `app/schemas/trace.py`

- status
- ended_at
- duration_ms
- metadata

## TraceSession
Source: `app/schemas/trace.py`

- id
- started_at
- ended_at
- created_at
- updated_at
- from_attributes

## TraceSessionList
Source: `app/schemas/trace.py`

- total
- items

## TraceSpanRecordBase
Source: `app/schemas/trace.py`

- trace_session_id
- span_id
- parent_span_id
- service_name
- operation_name
- duration_ms
- status_code
- status_message
- attributes
- logs

## TraceSpanRecordCreate
Source: `app/schemas/trace.py`

- (no parsed fields)

## TraceSpanRecord
Source: `app/schemas/trace.py`

- id
- start_time
- end_time
- created_at
- from_attributes

## TraceSpanRecordList
Source: `app/schemas/trace.py`

- total
- items

## TraceLinkBase
Source: `app/schemas/trace.py`

- from_trace_session_id
- to_trace_session_id
- to_span_id
- link_type
- metadata

## TraceLinkCreate
Source: `app/schemas/trace.py`

- (no parsed fields)

## TraceLink
Source: `app/schemas/trace.py`

- id
- created_at
- from_attributes

## UsageRecordBase
Source: `app/schemas/trace.py`

- tenant_id
- trace_session_id
- metric_name
- quantity
- unit
- cost
- period_start
- period_end
- metadata

## UsageRecordCreate
Source: `app/schemas/trace.py`

- (no parsed fields)

## UsageRecord
Source: `app/schemas/trace.py`

- id
- created_at
- from_attributes

## UsageRecordList
Source: `app/schemas/trace.py`

- total
- items

## MemorySpaceBase
Source: `app/schemas/memory.py`

- tenant_id
- scope_type
- scope_id
- name
- description
- metadata_json
- is_active

## MemorySpaceCreate
Source: `app/schemas/memory.py`

- (no parsed fields)

## MemorySpaceUpdate
Source: `app/schemas/memory.py`

- name
- description
- is_active

## MemorySpaceResponse
Source: `app/schemas/memory.py`

- id
- created_at
- updated_at

## MemorySpaceList
Source: `app/schemas/memory.py`

- items
- total

## MemoryEntryBase
Source: `app/schemas/memory.py`

- memory_space_id
- memory_type
- title
- content
- tags_json
- source_type
- source_id
- source_metadata_json
- metadata_json
- is_active

## MemoryEntryCreate
Source: `app/schemas/memory.py`

- (no parsed fields)

## MemoryEntryUpdate
Source: `app/schemas/memory.py`

- title
- content
- tags_json
- source_metadata_json
- metadata_json
- is_active

## MemoryEntryResponse
Source: `app/schemas/memory.py`

- id
- created_at
- updated_at

## MemoryEntryList
Source: `app/schemas/memory.py`

- items
- total

## MemoryResolveParams
Source: `app/schemas/memory.py`

- tenant_id
- organization_scope_id
- product_scope_id
- workflow_scope_id
- run_scope_id
- session_scope_id
- scope_type
- scope_id
- memory_type
- tags
- limit_per_scope
- is_active

## MemoryContextItem
Source: `app/schemas/memory.py`

- scope_type
- scope_id
- entries

## MemoryResolveResponse
Source: `app/schemas/memory.py`

- items
- total
- resolved_scopes
- context

## MemoryPersistRequest
Source: `app/schemas/memory.py`

- tenant_id
- scope_type
- scope_id
- memory_type
- title
- content
- tags
- source_type
- source_id
- source_metadata
- metadata
- space_name

## MemoryRunInspection
Source: `app/schemas/memory.py`

- run_id
- memory_context
- memory_read_ids
- memory_written_ids

## ComponentDefinitionCreate
Source: `app/schemas/component.py`

- name
- display_name
- description
- category
- icon

## ComponentDefinitionResponse
Source: `app/schemas/component.py`

- id
- name
- display_name
- description
- category
- icon
- created_at
- updated_at
- from_attributes

## ComponentDefinitionUpdate
Source: `app/schemas/component.py`

- name
- display_name
- description
- category
- icon

## ComponentVersionCreate
Source: `app/schemas/component.py`

- component_id
- version_number
- schema

## ComponentVersionResponse
Source: `app/schemas/component.py`

- id
- component_id
- version_number
- is_current
- schema
- created_at
- from_attributes

## ComponentCapabilityCreate
Source: `app/schemas/component.py`

- component_id
- capability_type
- capability_config

## ComponentCapabilityResponse
Source: `app/schemas/component.py`

- id
- component_id
- capability_type
- capability_config
- created_at
- from_attributes

## ComponentDefinitionListResponse
Source: `app/schemas/component.py`

- components
- total

## ComponentVersionListResponse
Source: `app/schemas/component.py`

- versions
- total

## ComponentCapabilityListResponse
Source: `app/schemas/component.py`

- capabilities
- total

## ComponentResolvedResponse
Source: `app/schemas/component.py`

- id
- name
- display_name
- description
- category
- icon
- current_version
- capabilities
- created_at
- updated_at

## TaskBase
Source: `app/schemas/task.py`

- title
- description
- status
- priority

## TaskCreate
Source: `app/schemas/task.py`

- tenant_id
- project_id
- assigned_to_employee_id
- assigned_to_agent_id

## TaskUpdate
Source: `app/schemas/task.py`

- title
- description
- status
- priority

## Task
Source: `app/schemas/task.py`

- id
- tenant_id
- project_id
- assigned_to_employee_id
- assigned_to_agent_id
- created_at
- updated_at

## TaskList
Source: `app/schemas/task.py`

- total
- items

## TaskCommentBase
Source: `app/schemas/task.py`

- content

## TaskCommentCreate
Source: `app/schemas/task.py`

- task_id
- author_type
- author_id

## TaskComment
Source: `app/schemas/task.py`

- id
- task_id
- author_type
- author_id
- created_at

## ExecutionRequestBase
Source: `app/schemas/task.py`

- goal
- capability
- quality

## ExecutionRequestCreate
Source: `app/schemas/task.py`

- tenant_id

## ExecutionRequestUpdate
Source: `app/schemas/task.py`

- status

## ExecutionRequest
Source: `app/schemas/task.py`

- id
- tenant_id
- status
- created_at
- started_at
- completed_at

## ExecutionRequestWithHistory
Source: `app/schemas/task.py`

- history

## ExecutionHistoryBase
Source: `app/schemas/task.py`

- event_type
- event_data

## ExecutionHistoryCreate
Source: `app/schemas/task.py`

- execution_request_id
- thread_id

## ExecutionHistory
Source: `app/schemas/task.py`

- id
- execution_request_id
- thread_id
- created_at

## ApprovalRequestBase
Source: `app/schemas/task.py`

- (no parsed fields)

## ApprovalRequestCreate
Source: `app/schemas/task.py`

- execution_request_id
- requested_by_type
- requested_by_id

## ApprovalRequestUpdate
Source: `app/schemas/task.py`

- status
- approver_notes

## ApprovalRequest
Source: `app/schemas/task.py`

- id
- execution_request_id
- status
- requested_by_type
- requested_by_id
- approver
- approver_notes
- requested_at
- decided_at

## ExecutionRequestList
Source: `app/schemas/task.py`

- total
- items

## BillingAdapterBindingBase
Source: `app/schemas/billing.py`

- tenant_id
- adapter_name
- adapter_type
- is_active
- config

## BillingAdapterBindingCreate
Source: `app/schemas/billing.py`

- (no parsed fields)

## BillingAdapterBinding
Source: `app/schemas/billing.py`

- id
- created_at
- updated_at
- from_attributes

## BillingAdapterBindingList
Source: `app/schemas/billing.py`

- total
- items

## BillingAccountBindingBase
Source: `app/schemas/billing.py`

- tenant_id
- adapter_binding_id
- external_account_id
- account_name
- status

## BillingAccountBindingCreate
Source: `app/schemas/billing.py`

- (no parsed fields)

## BillingAccountBindingBind
Source: `app/schemas/billing.py`

- adapter_binding_id
- external_account_id
- account_name

## BillingAccountBinding
Source: `app/schemas/billing.py`

- id
- created_at
- updated_at
- from_attributes

## BillingAccountBindingList
Source: `app/schemas/billing.py`

- total
- items

## BillingEventBase
Source: `app/schemas/billing.py`

- tenant_id
- account_binding_id
- event_type
- event_name
- quantity
- unit_price
- amount
- currency
- period_start
- period_end
- metadata

## BillingEventCreate
Source: `app/schemas/billing.py`

- (no parsed fields)

## BillingEvent
Source: `app/schemas/billing.py`

- id
- created_at
- from_attributes

## BillingEventList
Source: `app/schemas/billing.py`

- total
- items

## MeterDefinitionBase
Source: `app/schemas/billing.py`

- tenant_id
- meter_name
- display_name
- description
- unit
- unit_price
- aggregation_type
- is_active

## MeterDefinitionCreate
Source: `app/schemas/billing.py`

- (no parsed fields)

## MeterDefinition
Source: `app/schemas/billing.py`

- id
- created_at
- updated_at
- from_attributes

## MeterDefinitionList
Source: `app/schemas/billing.py`

- total
- items

## TemplatePackCreate
Source: `app/schemas/template.py`

- name
- description
- is_default

## TemplatePackResponse
Source: `app/schemas/template.py`

- id
- name
- description
- is_default
- created_at
- updated_at
- from_attributes

## TemplatePackUpdate
Source: `app/schemas/template.py`

- name
- description
- is_default

## WorkflowTemplateCreate
Source: `app/schemas/template.py`

- pack_id
- name
- description
- category
- tags

## WorkflowTemplateResponse
Source: `app/schemas/template.py`

- id
- pack_id
- name
- description
- category
- tags
- is_published
- published_version_id
- created_at
- updated_at
- from_attributes

## WorkflowTemplateUpdate
Source: `app/schemas/template.py`

- name
- description
- category
- tags
- is_published

## WorkflowTemplateVersionCreate
Source: `app/schemas/template.py`

- template_id
- runtime_spec

## WorkflowTemplateVersionResponse
Source: `app/schemas/template.py`

- id
- template_id
- version_number
- is_current
- runtime_spec
- created_at
- from_attributes

## TemplatePackListResponse
Source: `app/schemas/template.py`

- template_packs
- total

## WorkflowTemplateListResponse
Source: `app/schemas/template.py`

- templates
- total

## WorkflowTemplateVersionListResponse
Source: `app/schemas/template.py`

- versions
- total

## WorkflowTemplateResolvedResponse
Source: `app/schemas/template.py`

- id
- pack_id
- name
- description
- category
- tags
- is_published
- current_version
- published_version
- created_at
- updated_at

## ProductBase
Source: `app/schemas/collaboration.py`

- name
- strategy

## ProductCreate
Source: `app/schemas/collaboration.py`

- tenant_id

## ProductUpdate
Source: `app/schemas/collaboration.py`

- name
- strategy

## Product
Source: `app/schemas/collaboration.py`

- id
- tenant_id
- primary_channel_id
- created_at
- updated_at

## ProductList
Source: `app/schemas/collaboration.py`

- total
- items

## ProjectBase
Source: `app/schemas/collaboration.py`

- name
- start_date
- end_date

## ProjectCreate
Source: `app/schemas/collaboration.py`

- tenant_id

## ProjectUpdate
Source: `app/schemas/collaboration.py`

- name
- start_date
- end_date

## Project
Source: `app/schemas/collaboration.py`

- id
- tenant_id
- channel_id
- created_at
- updated_at

## ProjectList
Source: `app/schemas/collaboration.py`

- total
- items

## GroupBase
Source: `app/schemas/collaboration.py`

- name
- group_type

## GroupCreate
Source: `app/schemas/collaboration.py`

- tenant_id

## GroupUpdate
Source: `app/schemas/collaboration.py`

- name
- group_type

## Group
Source: `app/schemas/collaboration.py`

- id
- tenant_id
- primary_channel_id
- created_at
- updated_at

## GroupList
Source: `app/schemas/collaboration.py`

- total
- items

## GroupMembershipBase
Source: `app/schemas/collaboration.py`

- member_type
- member_id

## GroupMembershipCreate
Source: `app/schemas/collaboration.py`

- group_id

## GroupMembership
Source: `app/schemas/collaboration.py`

- id
- group_id
- joined_at
- ended_at

## ChannelBase
Source: `app/schemas/collaboration.py`

- name
- context_type
- context_id
- is_primary

## ChannelCreate
Source: `app/schemas/collaboration.py`

- tenant_id

## ChannelUpdate
Source: `app/schemas/collaboration.py`

- name
- is_primary

## Channel
Source: `app/schemas/collaboration.py`

- id
- tenant_id
- created_at
- updated_at

## ChannelList
Source: `app/schemas/collaboration.py`

- total
- items

## DecisionStatus
Source: `app/schemas/decision.py`

- DRAFT
- IN_REVIEW
- RECOMMENDED
- APPROVED
- REJECTED
- PROMOTED
- COMPLETED

## DecisionBase
Source: `app/schemas/decision.py`

- title
- description
- category
- status
- sponsor_type
- sponsor_id
- owner_type
- owner_id
- risk_level
- decision_scope

## DecisionCreate
Source: `app/schemas/decision.py`

- tenant_id
- project_id

## DecisionUpdate
Source: `app/schemas/decision.py`

- title
- description
- category
- status
- sponsor_type
- sponsor_id
- owner_type
- owner_id
- risk_level
- decision_scope
- project_id
- recommended_alternative_id

## Decision
Source: `app/schemas/decision.py`

- id
- tenant_id
- project_id
- recommended_alternative_id
- created_at
- updated_at

## DecisionList
Source: `app/schemas/decision.py`

- total
- items

## DecisionAlternativeBase
Source: `app/schemas/decision.py`

- title
- description
- status
- estimated_cost
- estimated_time_days

## DecisionAlternativeCreate
Source: `app/schemas/decision.py`

- decision_id

## DecisionAlternativeUpdate
Source: `app/schemas/decision.py`

- title
- description
- status
- estimated_cost
- estimated_time_days

## DecisionAlternative
Source: `app/schemas/decision.py`

- id
- decision_id
- created_at

## DecisionAlternativeList
Source: `app/schemas/decision.py`

- total
- items

## DecisionEvidenceBase
Source: `app/schemas/decision.py`

- title
- evidence_type
- source_type
- source_id
- summary
- url_or_path

## DecisionEvidenceCreate
Source: `app/schemas/decision.py`

- decision_id

## DecisionEvidenceUpdate
Source: `app/schemas/decision.py`

- title
- evidence_type
- source_type
- source_id
- summary
- url_or_path

## DecisionEvidence
Source: `app/schemas/decision.py`

- id
- decision_id
- created_at

## DecisionEvidenceList
Source: `app/schemas/decision.py`

- total
- items

## DecisionCriterionBase
Source: `app/schemas/decision.py`

- name
- description
- weight
- scoring_method

## DecisionCriterionCreate
Source: `app/schemas/decision.py`

- decision_id

## DecisionCriterionUpdate
Source: `app/schemas/decision.py`

- name
- description
- weight
- scoring_method

## DecisionCriterion
Source: `app/schemas/decision.py`

- id
- decision_id
- created_at

## DecisionCriterionList
Source: `app/schemas/decision.py`

- total
- items

## DecisionScoreBase
Source: `app/schemas/decision.py`

- score
- rationale

## DecisionScoreCreate
Source: `app/schemas/decision.py`

- decision_id
- alternative_id
- criterion_id

## DecisionScoreUpdate
Source: `app/schemas/decision.py`

- score
- rationale

## DecisionScore
Source: `app/schemas/decision.py`

- id
- decision_id
- alternative_id
- criterion_id
- created_at

## DecisionScoreList
Source: `app/schemas/decision.py`

- total
- items

## DecisionRecommendationBase
Source: `app/schemas/decision.py`

- summary
- rationale
- tradeoffs
- generated_by_type
- generated_by_id

## DecisionRecommendationCreate
Source: `app/schemas/decision.py`

- decision_id
- recommended_alternative_id

## DecisionRecommendationUpdate
Source: `app/schemas/decision.py`

- summary
- rationale
- tradeoffs
- recommended_alternative_id

## DecisionRecommendation
Source: `app/schemas/decision.py`

- id
- decision_id
- recommended_alternative_id
- created_at

## DecisionRecommendationList
Source: `app/schemas/decision.py`

- total
- items

## DecisionApprovalStepBase
Source: `app/schemas/decision.py`

- approver_type
- approver_id
- status
- sequence_order
- notes

## DecisionApprovalStepCreate
Source: `app/schemas/decision.py`

- decision_id

## DecisionApprovalStepUpdate
Source: `app/schemas/decision.py`

- approver_type
- approver_id
- status
- notes

## DecisionApprovalStep
Source: `app/schemas/decision.py`

- id
- decision_id
- decided_at
- created_at

## DecisionApprovalStepList
Source: `app/schemas/decision.py`

- total
- items

## DecisionOutcomeReviewBase
Source: `app/schemas/decision.py`

- review_date
- outcome_status
- expected_vs_actual
- lessons_learned
- reviewed_by

## DecisionOutcomeReviewCreate
Source: `app/schemas/decision.py`

- decision_id

## DecisionOutcomeReviewUpdate
Source: `app/schemas/decision.py`

- review_date
- outcome_status
- expected_vs_actual
- lessons_learned
- reviewed_by

## DecisionOutcomeReview
Source: `app/schemas/decision.py`

- id
- decision_id
- created_at

## DecisionOutcomeReviewList
Source: `app/schemas/decision.py`

- total
- items

## DecisionEvent
Source: `app/schemas/decision.py`

- id
- decision_id
- event_type
- event_data
- created_at

## DecisionEventList
Source: `app/schemas/decision.py`

- total
- items

## DecisionDetail
Source: `app/schemas/decision.py`

- id
- tenant_id
- project_id
- title
- description
- category
- status
- sponsor_type
- sponsor_id
- owner_type
- owner_id
- risk_level
- decision_scope
- recommended_alternative_id
- created_at
- updated_at
- alternatives
- evidence
- criteria
- recommendation
- approval_steps
- outcome_reviews
- events

## EmployeeBase
Source: `app/schemas/employee.py`

- name
- email

## EmployeeCreate
Source: `app/schemas/employee.py`

- tenant_id

## EmployeeUpdate
Source: `app/schemas/employee.py`

- name
- email

## Employee
Source: `app/schemas/employee.py`

- id
- tenant_id
- created_at
- updated_at

## EmployeeWithIdentity
Source: `app/schemas/employee.py`

- current_identity

## EmployeeIdentityBase
Source: `app/schemas/employee.py`

- job_title
- department
- seniority
- reporting_to_employee_id

## EmployeeIdentityCreate
Source: `app/schemas/employee.py`

- employee_id

## EmployeeIdentity
Source: `app/schemas/employee.py`

- id
- employee_id
- effective_from
- effective_to

## EmployeeList
Source: `app/schemas/employee.py`

- total
- items

## ExecutionIdentityBindingBase
Source: `app/schemas/execution_identity.py`

- provider_name
- workflow_id
- workflow_version_id
- template_id
- external_identity_id
- tenant_id
- agent_name
- agent_type
- sponsor_id
- owner_ids_json
- manager_id
- blueprint_id
- allowed_models_json
- budget_limit
- tpm_limit
- expires_at
- status

## ExecutionIdentityBindingCreate
Source: `app/schemas/execution_identity.py`

- (no parsed fields)

## ExecutionIdentityBindingUpdate
Source: `app/schemas/execution_identity.py`

- workflow_id
- workflow_version_id
- template_id
- status
- metadata_json

## ExecutionIdentityBindingResponse
Source: `app/schemas/execution_identity.py`

- id
- last_synced_at
- metadata_json
- created_at
- updated_at

## ExecutionIdentityBindingDetail
Source: `app/schemas/execution_identity.py`

- (no parsed fields)

## PolicyEvaluationResultBase
Source: `app/schemas/execution_identity.py`

- provider_name
- workflow_id
- workflow_version_id
- run_id
- external_identity_id
- evaluation_type
- is_allowed
- reasons_json
- metadata_json

## PolicyEvaluationResultCreate
Source: `app/schemas/execution_identity.py`

- (no parsed fields)

## PolicyEvaluationResultResponse
Source: `app/schemas/execution_identity.py`

- id
- created_at

## ExecutionIdentityBindingList
Source: `app/schemas/execution_identity.py`

- items
- total

## SkillDefinitionBase
Source: `app/schemas/skill.py`

- tenant_id
- scope_type
- scope_id
- name
- slug
- description
- skill_type
- status

## SkillDefinitionCreate
Source: `app/schemas/skill.py`

- (no parsed fields)

## SkillDefinitionUpdate
Source: `app/schemas/skill.py`

- name
- description
- status

## SkillDefinitionResponse
Source: `app/schemas/skill.py`

- id
- created_at
- updated_at

## SkillDefinitionList
Source: `app/schemas/skill.py`

- items
- total

## SkillVersionBase
Source: `app/schemas/skill.py`

- skill_id
- version_number
- content_json
- input_schema_json
- output_schema_json
- tool_requirements_json
- metadata_json
- is_current

## SkillVersionCreate
Source: `app/schemas/skill.py`

- (no parsed fields)

## SkillVersionUpdate
Source: `app/schemas/skill.py`

- is_current

## SkillVersionResponse
Source: `app/schemas/skill.py`

- id
- created_at

## SkillVersionList
Source: `app/schemas/skill.py`

- items
- total

## SkillBindingBase
Source: `app/schemas/skill.py`

- skill_id
- workflow_id
- template_id
- component_id
- agent_role
- binding_type

## SkillBindingCreate
Source: `app/schemas/skill.py`

- (no parsed fields)

## SkillBindingResponse
Source: `app/schemas/skill.py`

- id
- created_at

## SkillBindingList
Source: `app/schemas/skill.py`

- items
- total

## SkillPromotionRecordBase
Source: `app/schemas/skill.py`

- source_type
- source_id
- skill_id
- promoted_by
- reason
- evidence_json

## SkillPromotionRecordCreate
Source: `app/schemas/skill.py`

- (no parsed fields)

## SkillPromotionRecordResponse
Source: `app/schemas/skill.py`

- id
- created_at

## SkillPromotionRecordList
Source: `app/schemas/skill.py`

- items
- total

## SkillResolveParams
Source: `app/schemas/skill.py`

- tenant_id
- scope_type
- scope_id
- workflow_id
- template_id
- component_id
- agent_role

## SkillResolveResponse
Source: `app/schemas/skill.py`

- items
- total
- resolved_scopes

## Tenant
Source: `app/models/tenant_employee.py`

- __tablename__
- id
- name
- enabled
- created_at
- updated_at

## Employee
Source: `app/models/tenant_employee.py`

- __tablename__
- id
- tenant_id
- email
- name
- created_at
- updated_at
- tenant

## EmployeeIdentity
Source: `app/models/tenant_employee.py`

- __tablename__
- id
- employee_id
- job_title
- department
- seniority
- reporting_to_employee_id
- effective_from
- effective_to
- employee

## EmployeeEmployment
Source: `app/models/tenant_employee.py`

- __tablename__
- id
- employee_id
- start_date
- end_date
- employment_type
- created_at

## EmployeeEducation
Source: `app/models/tenant_employee.py`

- __tablename__
- id
- employee_id
- institution
- degree
- field_of_study
- start_date
- end_date

## EmployeeCertification
Source: `app/models/tenant_employee.py`

- __tablename__
- id
- employee_id
- certification_code
- certification_name
- issued_date
- expiry_date

## Agent
Source: `app/models/agent.py`

- __tablename__
- id
- tenant_id
- name
- agent_type
- is_primary
- created_at
- updated_at
- tenant

## AgentIdentity
Source: `app/models/agent.py`

- __tablename__
- id
- agent_id
- projected_title
- projected_department
- effective_from
- effective_to
- agent

## AgentProfile
Source: `app/models/agent.py`

- __tablename__
- id
- agent_id
- behavioral_profile
- operational_profile
- agent

## AgentSkill
Source: `app/models/agent.py`

- __tablename__
- id
- agent_id
- skill_code
- skill_name
- proficiency_level
- evidence
- last_assessed
- agent

## AgentGovernanceProfile
Source: `app/models/agent.py`

- __tablename__
- id
- agent_id
- prompt_profile_id
- guardrail_profile_id
- approval_profile_id
- channel_profile_id
- agent

## AgentMemoryProfile
Source: `app/models/agent.py`

- __tablename__
- id
- agent_id
- memory_enabled
- thread_retention_days
- checkpoint_interval_seconds
- agent

## AgentRelationship
Source: `app/models/agent.py`

- __tablename__
- id
- from_agent_id
- from_employee_id
- to_agent_id
- to_employee_id
- relationship_type
- from_agent
- to_agent

## EmployeeAgentAssignment
Source: `app/models/agent.py`

- __tablename__
- id
- employee_id
- agent_id
- assignment_role
- assigned_at
- ended_at
- employee
- agent

## PromptTemplate
Source: `app/models/prompt_skills_goals_timelines.py`

- __tablename__
- id
- profile_id
- name
- content
- description
- is_active
- created_at
- updated_at

## PromptTemplateVersion
Source: `app/models/prompt_skills_goals_timelines.py`

- __tablename__
- id
- template_id
- version
- content
- change_note
- created_at
- created_by

## AgentPromptAssignment
Source: `app/models/prompt_skills_goals_timelines.py`

- __tablename__
- id
- agent_id
- prompt_template_id
- assigned_at
- assigned_by
- ended_at

## SkillProfile
Source: `app/models/prompt_skills_goals_timelines.py`

- __tablename__
- id
- name
- description
- is_default
- created_at
- updated_at

## SkillProfileSkill
Source: `app/models/prompt_skills_goals_timelines.py`

- __tablename__
- id
- profile_id
- skill_code
- proficiency_level
- is_core
- created_at

## AgentGoal
Source: `app/models/prompt_skills_goals_timelines.py`

- __tablename__
- id
- agent_id
- goal_type
- description
- target_date
- created_at
- agent

## GoalSuccessCriteria
Source: `app/models/prompt_skills_goals_timelines.py`

- __tablename__
- id
- goal_id
- criteria_type
- criteria_value
- weight
- created_at

## GoalConstraint
Source: `app/models/prompt_skills_goals_timelines.py`

- __tablename__
- id
- goal_id
- constraint_type
- constraint_value
- created_at

## Timeline
Source: `app/models/prompt_skills_goals_timelines.py`

- __tablename__
- id
- agent_id
- name
- start_date
- end_date
- status
- created_at
- updated_at
- agent

## TimelineMilestone
Source: `app/models/prompt_skills_goals_timelines.py`

- __tablename__
- id
- timeline_id
- name
- target_date
- status
- description
- created_at
- updated_at

## TimelineDeadline
Source: `app/models/prompt_skills_goals_timelines.py`

- __tablename__
- id
- timeline_id
- name
- due_at
- reminder_at
- description
- created_at

## TimelineDependency
Source: `app/models/prompt_skills_goals_timelines.py`

- __tablename__
- id
- timeline_id
- depends_on_timeline_id
- dependency_type
- created_at

## AgentGroupMembership
Source: `app/models/prompt_skills_goals_timelines.py`

- __tablename__
- id
- group_id
- agent_id
- role
- joined_at
- ended_at

## ExecutionRequest
Source: `app/models/control_plane.py`

- __tablename__
- id
- tenant_id
- goal
- capability
- quality
- status
- created_at
- started_at
- completed_at
- tenant
- request_metadata
- history
- approvals

## ExecutionRequestMetadata
Source: `app/models/control_plane.py`

- __tablename__
- id
- execution_request_id
- key
- value
- execution_request

## ExecutionHistory
Source: `app/models/control_plane.py`

- __tablename__
- id
- execution_request_id
- thread_id
- event_type
- event_data
- created_at
- execution_request

## PolicyResolution
Source: `app/models/control_plane.py`

- __tablename__
- id
- execution_request_id
- policy_id
- default_decision
- decision_reason

## BackendSelection
Source: `app/models/control_plane.py`

- __tablename__
- id
- execution_request_id
- selected_backend
- selection_order
- selected_at

## FallbackEvent
Source: `app/models/control_plane.py`

- __tablename__
- id
- execution_request_id
- from_backend
- to_backend
- reason
- triggered_at

## ApprovalRequest
Source: `app/models/control_plane.py`

- __tablename__
- id
- execution_request_id
- status
- requested_by_type
- requested_by_id
- approver
- approver_notes
- requested_at
- decided_at
- execution_request

## DecisionRecord
Source: `app/models/control_plane.py`

- __tablename__
- id
- execution_request_id
- decision_type
- decision_reason
- decided_at

## OverrideRecord
Source: `app/models/control_plane.py`

- __tablename__
- id
- execution_request_id
- override_type
- reason
- applied_by
- effective_from
- effective_to
- status

## ResponsibilityAssignment
Source: `app/models/control_plane.py`

- __tablename__
- id
- assignment_type
- from_type
- from_id
- to_type
- to_id
- reason
- effective_from
- effective_to
- status

## UsageRecord
Source: `app/models/control_plane.py`

- __tablename__
- id
- execution_request_id
- backend_used
- provider
- model
- input_tokens
- output_tokens
- total_tokens
- cost
- latency_ms

## MemoryCheckpoint
Source: `app/models/control_plane.py`

- __tablename__
- id
- execution_request_id
- thread_id
- checkpoint_data
- created_at

## TenantPolicy
Source: `app/models/control_plane.py`

- __tablename__
- id
- tenant_id
- name
- enabled
- quality_default
- allow_fallback
- max_retries
- approval_required_for
- max_budget_monthly
- max_requests_per_hour
- created_at
- updated_at
- tenant

## TenantPolicyBackendRule
Source: `app/models/control_plane.py`

- __tablename__
- id
- policy_id
- backend_id
- rule_action
- reason
- created_at

## TenantCapabilityPolicy
Source: `app/models/control_plane.py`

- __tablename__
- id
- policy_id
- capability
- max_tokens_per_request
- max_images_per_month
- rate_limit_per_hour
- created_at
- updated_at

## TraceSession
Source: `app/models/trace.py`

- __tablename__
- id
- tenant_id
- trace_id
- session_type
- status
- started_at
- ended_at
- duration_ms
- metadata
- created_at
- updated_at
- tenant

## TraceSpanRecord
Source: `app/models/trace.py`

- __tablename__
- id
- trace_session_id
- span_id
- parent_span_id
- service_name
- operation_name
- start_time
- end_time
- duration_ms
- status_code
- status_message
- attributes
- logs
- created_at
- trace_session

## TraceLink
Source: `app/models/trace.py`

- __tablename__
- id
- from_trace_session_id
- to_trace_session_id
- to_span_id
- link_type
- metadata
- created_at
- from_session
- to_session

## UsageRecord
Source: `app/models/trace.py`

- __tablename__
- id
- tenant_id
- trace_session_id
- metric_name
- quantity
- unit
- cost
- period_start
- period_end
- metadata
- created_at
- tenant
- trace_session

## MemorySpace
Source: `app/models/memory.py`

- __tablename__
- id
- tenant_id
- scope_type
- scope_id
- name
- description
- metadata_json
- is_active
- created_at
- updated_at

## MemoryEntry
Source: `app/models/memory.py`

- __tablename__
- id
- memory_space_id
- memory_type
- title
- content
- tags_json
- source_type
- source_id
- source_metadata_json
- metadata_json
- is_active
- created_at
- updated_at

## ComponentDefinition
Source: `app/models/component.py`

- __tablename__
- id
- name
- display_name
- description
- category
- icon
- created_at
- updated_at
- versions
- capabilities

## ComponentVersion
Source: `app/models/component.py`

- __tablename__
- id
- component_id
- version_number
- is_current
- schema_json
- created_at
- component

## ComponentCapability
Source: `app/models/component.py`

- __tablename__
- id
- component_id
- capability_type
- capability_config
- created_at
- component

## WorkflowDefinition
Source: `app/models/workflow_definition.py`

- __tablename__
- id
- tenant_id
- name
- description
- source_type
- source_json
- is_published
- published_version_id
- created_at
- updated_at
- tenant
- versions

## WorkflowVersion
Source: `app/models/workflow_definition.py`

- __tablename__
- id
- workflow_id
- version_number
- is_current
- runtime_spec
- created_at
- workflow
- nodes
- edges

## WorkflowNode
Source: `app/models/workflow_definition.py`

- __tablename__
- id
- version_id
- node_type
- node_id
- label
- config
- position_x
- position_y
- created_at
- version

## WorkflowEdge
Source: `app/models/workflow_definition.py`

- __tablename__
- id
- version_id
- edge_id
- source_node_id
- target_node_id
- edge_type
- label
- condition
- created_at
- version

## WorkflowValidationResult
Source: `app/models/workflow_definition.py`

- __tablename__
- id
- workflow_id
- version_id
- is_valid
- issues_json
- can_publish
- created_at
- workflow

## WorkflowPublishArtifact
Source: `app/models/workflow_definition.py`

- __tablename__
- id
- workflow_id
- version_id
- artifact_json
- created_at
- workflow

## WorkflowRun
Source: `app/models/workflow_definition.py`

- __tablename__
- id
- workflow_id
- version_id
- status
- final_output
- memory_context_json
- resolved_skills_json
- started_at
- completed_at
- error_message
- memory_read_ids_json
- memory_written_ids_json
- memory_write_mode
- workflow
- steps

## WorkflowRunStep
Source: `app/models/workflow_definition.py`

- __tablename__
- id
- run_id
- node_id
- node_type
- status
- output
- error
- branch_decision
- started_at
- completed_at
- run

## Task
Source: `app/models/workflow.py`

- __tablename__
- id
- tenant_id
- project_id
- title
- description
- status
- priority
- assigned_to_employee_id
- assigned_to_agent_id
- created_at
- updated_at
- tenant
- project
- comments
- attachments

## TaskDependency
Source: `app/models/workflow.py`

- __tablename__
- id
- task_id
- depends_on_task_id
- dependency_type
- task

## TaskAssignmentHistory
Source: `app/models/workflow.py`

- __tablename__
- id
- task_id
- assigned_from_type
- assigned_from_id
- assigned_to_type
- assigned_to_id
- assigned_by
- assigned_at

## Milestone
Source: `app/models/workflow.py`

- __tablename__
- id
- project_id
- name
- target_date
- status
- created_at
- updated_at
- project

## MilestoneTask
Source: `app/models/workflow.py`

- __tablename__
- id
- milestone_id
- task_id

## Deadline
Source: `app/models/workflow.py`

- __tablename__
- id
- task_id
- due_at
- reminder_at

## Escalation
Source: `app/models/workflow.py`

- __tablename__
- id
- entity_type
- entity_id
- escalation_type
- reason
- escalated_to
- status
- created_at
- updated_at

## Reminder
Source: `app/models/workflow.py`

- __tablename__
- id
- reminder_type
- entity_type
- entity_id
- remind_at
- message
- status
- created_at

## TaskComment
Source: `app/models/workflow.py`

- __tablename__
- id
- task_id
- author_type
- author_id
- content
- parent_comment_id
- created_at
- task

## TaskAttachment
Source: `app/models/workflow.py`

- __tablename__
- id
- task_id
- file_asset_id
- uploaded_by
- created_at
- task

## TaskCommentAttachment
Source: `app/models/workflow.py`

- __tablename__
- id
- task_comment_id
- file_asset_id

## TaskRating
Source: `app/models/workflow.py`

- __tablename__
- id
- task_id
- rating_type
- score
- rated_by
- created_at

## TaskFeedback
Source: `app/models/workflow.py`

- __tablename__
- id
- task_id
- content
- provided_by
- created_at

## BillingAdapterBinding
Source: `app/models/billing.py`

- __tablename__
- id
- tenant_id
- adapter_name
- adapter_type
- is_active
- config
- created_at
- updated_at
- tenant

## BillingAccountBinding
Source: `app/models/billing.py`

- __tablename__
- id
- tenant_id
- adapter_binding_id
- external_account_id
- account_name
- status
- created_at
- updated_at
- tenant
- adapter_binding

## BillingEvent
Source: `app/models/billing.py`

- __tablename__
- id
- tenant_id
- account_binding_id
- event_type
- event_name
- quantity
- unit_price
- amount
- currency
- period_start
- period_end
- metadata
- created_at
- tenant
- account_binding

## MeterDefinition
Source: `app/models/billing.py`

- __tablename__
- id
- tenant_id
- meter_name
- display_name
- description
- unit
- unit_price
- aggregation_type
- is_active
- created_at
- updated_at
- tenant

## TemplatePack
Source: `app/models/template.py`

- __tablename__
- id
- name
- description
- is_default
- created_at
- updated_at
- templates

## WorkflowTemplate
Source: `app/models/template.py`

- __tablename__
- id
- pack_id
- name
- description
- category
- tags
- is_published
- published_version_id
- created_at
- updated_at
- pack
- versions

## WorkflowTemplateVersion
Source: `app/models/template.py`

- __tablename__
- id
- template_id
- version_number
- is_current
- runtime_spec
- created_at
- template

## DepartmentMaster
Source: `app/models/master_data.py`

- __tablename__
- code
- name
- parent_department_code
- created_at

## JobTitleMaster
Source: `app/models/master_data.py`

- __tablename__
- code
- name
- created_at

## SeniorityLevelMaster
Source: `app/models/master_data.py`

- __tablename__
- code
- name
- level_order
- created_at

## SfiaSkillMaster
Source: `app/models/master_data.py`

- __tablename__
- code
- name
- category
- created_at

## CertificationMaster
Source: `app/models/master_data.py`

- __tablename__
- code
- name
- provider
- created_at

## InstitutionMaster
Source: `app/models/master_data.py`

- __tablename__
- code
- name
- institution_type
- created_at

## QualificationTypeMaster
Source: `app/models/master_data.py`

- __tablename__
- code
- name
- created_at

## TopicMaster
Source: `app/models/master_data.py`

- __tablename__
- code
- name
- created_at

## PromptProfileMaster
Source: `app/models/master_data.py`

- __tablename__
- id
- name
- description
- is_default
- created_at
- updated_at

## GuardrailProfileMaster
Source: `app/models/master_data.py`

- __tablename__
- id
- name
- rules
- created_at
- updated_at

## ApprovalProfileMaster
Source: `app/models/master_data.py`

- __tablename__
- id
- name
- rules
- created_at
- updated_at

## ChannelProfileMaster
Source: `app/models/master_data.py`

- __tablename__
- id
- name
- settings
- created_at
- updated_at

## Product
Source: `app/models/collaboration.py`

- __tablename__
- id
- tenant_id
- name
- strategy
- primary_channel_id
- created_at
- updated_at
- tenant

## Project
Source: `app/models/collaboration.py`

- __tablename__
- id
- tenant_id
- name
- start_date
- end_date
- channel_id
- created_at
- updated_at
- tenant

## GroupEntity
Source: `app/models/collaboration.py`

- __tablename__
- id
- tenant_id
- name
- group_type
- primary_channel_id
- created_at
- updated_at
- tenant
- memberships

## GroupMembership
Source: `app/models/collaboration.py`

- __tablename__
- id
- group_id
- member_type
- member_id
- joined_at
- ended_at
- group

## Channel
Source: `app/models/collaboration.py`

- __tablename__
- id
- tenant_id
- context_type
- context_id
- name
- is_primary
- created_at
- updated_at
- tenant
- memberships
- messages

## ChannelMembership
Source: `app/models/collaboration.py`

- __tablename__
- id
- channel_id
- member_type
- member_id
- role
- joined_at
- ended_at
- channel

## ChannelMessage
Source: `app/models/collaboration.py`

- __tablename__
- id
- channel_id
- author_type
- author_id
- content
- created_at
- channel

## FileAsset
Source: `app/models/collaboration.py`

- __tablename__
- id
- tenant_id
- uploaded_by_type
- uploaded_by_id
- file_name
- file_path
- file_size
- mime_type
- created_at

## ChannelFile
Source: `app/models/collaboration.py`

- __tablename__
- id
- channel_id
- file_asset_id
- uploaded_by
- created_at

## Decision
Source: `app/models/decision.py`

- __tablename__
- id
- tenant_id
- project_id
- title
- description
- category
- status
- sponsor_type
- sponsor_id
- owner_type
- owner_id
- risk_level
- decision_scope
- recommended_alternative_id
- created_at
- updated_at
- tenant
- project
- alternatives
- back_populates
- cascade
- foreign_keys
- evidence
- criteria
- scores
- recommendations
- approval_steps
- outcome_reviews
- events
- recommended_alternative
- uselist

## DecisionAlternative
Source: `app/models/decision.py`

- __tablename__
- id
- decision_id
- title
- description
- status
- estimated_cost
- estimated_time_days
- created_at
- decision
- scores

## DecisionEvidence
Source: `app/models/decision.py`

- __tablename__
- id
- decision_id
- evidence_type
- source_type
- source_id
- title
- summary
- url_or_path
- created_at
- decision

## DecisionCriterion
Source: `app/models/decision.py`

- __tablename__
- id
- decision_id
- name
- description
- weight
- scoring_method
- created_at
- decision
- scores

## DecisionScore
Source: `app/models/decision.py`

- __tablename__
- id
- decision_id
- alternative_id
- criterion_id
- score
- rationale
- created_at
- decision
- alternative
- criterion

## DecisionRecommendation
Source: `app/models/decision.py`

- __tablename__
- id
- decision_id
- recommended_alternative_id
- summary
- rationale
- tradeoffs
- generated_by_type
- generated_by_id
- created_at
- decision
- recommended_alternative
- foreign_keys

## DecisionApprovalStep
Source: `app/models/decision.py`

- __tablename__
- id
- decision_id
- approver_type
- approver_id
- status
- sequence_order
- notes
- decided_at
- created_at
- decision

## DecisionOutcomeReview
Source: `app/models/decision.py`

- __tablename__
- id
- decision_id
- review_date
- outcome_status
- expected_vs_actual
- lessons_learned
- reviewed_by
- created_at
- decision

## DecisionEvent
Source: `app/models/decision.py`

- __tablename__
- id
- decision_id
- event_type
- event_data
- created_at
- decision

## ExecutionIdentityBinding
Source: `app/models/execution_identity.py`

- __tablename__
- id
- provider_name
- workflow_id
- workflow_version_id
- template_id
- external_identity_id
- tenant_id
- agent_name
- agent_type
- sponsor_id
- owner_ids_json
- manager_id
- blueprint_id
- allowed_models_json
- budget_limit
- tpm_limit
- expires_at
- status
- last_synced_at
- metadata_json
- created_at
- updated_at

## PolicyEvaluationResult
Source: `app/models/execution_identity.py`

- __tablename__
- id
- provider_name
- workflow_id
- workflow_version_id
- run_id
- external_identity_id
- evaluation_type
- is_allowed
- reasons_json
- metadata_json
- created_at

## SkillDefinition
Source: `app/models/skill.py`

- __tablename__
- id
- tenant_id
- scope_type
- scope_id
- name
- slug
- description
- skill_type
- status
- created_at
- updated_at

## SkillVersion
Source: `app/models/skill.py`

- __tablename__
- id
- skill_id
- version_number
- content_json
- input_schema_json
- output_schema_json
- tool_requirements_json
- metadata_json
- is_current
- created_at

## SkillBinding
Source: `app/models/skill.py`

- __tablename__
- id
- skill_id
- workflow_id
- template_id
- component_id
- agent_role
- binding_type
- created_at

## SkillPromotionRecord
Source: `app/models/skill.py`

- __tablename__
- id
- source_type
- source_id
- skill_id
- promoted_by
- reason
- evidence_json
- created_at

