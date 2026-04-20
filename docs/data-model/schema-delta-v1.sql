-- Autonomyx Decide Schema Delta v1
-- Content-type-aware review, workflow templates, ITSM/CMDB, enterprise processes
--
-- This file contains ONLY additions and updates to schema-v2-complete.sql
-- Run this AFTER schema-v2-complete.sql
--
-- Delta version: v1
-- ============================================

-- ============================================
-- DELTA 1: CONTENT-TYPE-AWARE REVIEW WORKFLOW
-- Master tables
-- ============================================

-- master_document_type
CREATE TABLE master_document_type (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(80) UNIQUE NOT NULL,
    name VARCHAR(160) NOT NULL,
    schema_org_type VARCHAR(120) NULL,
    creative_work_kind VARCHAR(120) NULL,
    review_required_by_default BOOLEAN NOT NULL DEFAULT FALSE,
    retention_policy_days INTEGER NULL,
    allowed_mime_patterns JSONB NOT NULL DEFAULT '[]'::jsonb,
    allowed_file_exts JSONB NOT NULL DEFAULT '[]'::jsonb,
    metadata_schema_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL
);

CREATE INDEX idx_master_doc_type_code ON master_document_type(code);

-- master_content_type
CREATE TABLE master_content_type (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(80) UNIQUE NOT NULL,
    name VARCHAR(160) NOT NULL,
    schema_org_type VARCHAR(120) NULL,
    parent_content_type_id UUID NULL REFERENCES master_content_type(id),
    default_workflow_template_id UUID NULL,
    default_review_policy_id UUID NULL,
    rendering_hint VARCHAR(80) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL
);

CREATE INDEX idx_master_content_type_code ON master_content_type(code);
CREATE INDEX idx_master_content_parent ON master_content_type(parent_content_type_id);

-- master_action
CREATE TABLE master_action (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(80) UNIQUE NOT NULL,
    name VARCHAR(160) NOT NULL,
    schema_org_action_type VARCHAR(120) NULL,
    action_category VARCHAR(80) NOT NULL,
    default_subject_type VARCHAR(80) NULL,
    default_result_type VARCHAR(80) NULL,
    requires_review BOOLEAN NOT NULL DEFAULT FALSE,
    requires_approval BOOLEAN NOT NULL DEFAULT FALSE,
    is_user_visible BOOLEAN NOT NULL DEFAULT TRUE,
    is_system_action BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL
);

CREATE INDEX idx_master_action_code ON master_action(code);
CREATE INDEX idx_master_action_category ON master_action(action_category);

-- master_resource_type
CREATE TABLE master_resource_type (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(80) UNIQUE NOT NULL,
    name VARCHAR(160) NOT NULL,
    resource_category VARCHAR(80) NOT NULL,
    schema_org_type VARCHAR(120) NULL,
    capacity_unit VARCHAR(40) NULL,
    is_allocatable BOOLEAN NOT NULL DEFAULT TRUE,
    is_asset BOOLEAN NOT NULL DEFAULT FALSE,
    is_service BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL
);

CREATE INDEX idx_master_resource_type_code ON master_resource_type(code);
CREATE INDEX idx_master_resource_category ON master_resource_type(resource_category);

-- master_template_type
CREATE TABLE master_template_type (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(80) UNIQUE NOT NULL,
    name VARCHAR(160) NOT NULL,
    template_scope VARCHAR(80) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL
);

-- ============================================
-- DELTA 1: CONTENT-TYPE-AWARE REVIEW WORKFLOW
-- Operational tables
-- ============================================

-- content_item
CREATE TABLE content_item (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    content_type_id UUID NOT NULL,
    document_type_id UUID NULL REFERENCES master_document_type(id),
    title VARCHAR(240) NOT NULL,
    slug VARCHAR(240) NULL,
    summary_text TEXT NULL,
    body_text TEXT NULL,
    body_json JSONB NULL,
    creative_work_status VARCHAR(80) NULL,
    language_code VARCHAR(20) NULL,
    owner_identity_id UUID NULL,
    author_identity_id UUID NULL,
    accountable_identity_id UUID NULL,
    current_version_id UUID NULL,
    primary_file_asset_id UUID NULL,
    schema_org_type VARCHAR(120) NULL,
    visibility_scope VARCHAR(80) NULL,
    published_at TIMESTAMPTZ NULL,
    expires_at TIMESTAMPTZ NULL,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL
);

CREATE INDEX idx_content_item_tenant ON content_item(tenant_id);
CREATE INDEX idx_content_item_type ON content_item(content_type_id);
CREATE INDEX idx_content_item_owner ON content_item(owner_identity_id);
CREATE INDEX idx_content_item_status ON content_item(creative_work_status);

-- content_version
CREATE TABLE content_version (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    content_item_id UUID NOT NULL REFERENCES content_item(id),
    version_label VARCHAR(80) NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    change_summary TEXT NULL,
    body_text TEXT NULL,
    body_json JSONB NULL,
    primary_file_asset_id UUID NULL,
    checksum_sha256 VARCHAR(64) NULL,
    created_by_identity_id UUID NULL,
    published_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(content_item_id, version_label)
);

CREATE INDEX idx_content_version_item ON content_version(content_item_id);

-- content_subject_link
CREATE TABLE content_subject_link (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    content_item_id UUID NOT NULL REFERENCES content_item(id),
    subject_type VARCHAR(80) NOT NULL,
    subject_id UUID NOT NULL,
    relationship_type VARCHAR(80) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(content_item_id, subject_type, subject_id, relationship_type)
);

CREATE INDEX idx_content_link_item ON content_subject_link(content_item_id);
CREATE INDEX idx_content_link_subject ON content_subject_link(subject_type, subject_id);

-- review_workflow
CREATE TABLE review_workflow (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    subject_type VARCHAR(80) NOT NULL,
    subject_id UUID NOT NULL,
    content_item_id UUID NULL REFERENCES content_item(id),
    workflow_template_id UUID NULL,
    review_type VARCHAR(80) NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'open',
    requested_by_identity_id UUID NOT NULL,
    owner_identity_id UUID NULL,
    opened_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at TIMESTAMPTZ NULL,
    review_notes TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX idx_review_workflow_tenant ON review_workflow(tenant_id);
CREATE INDEX idx_review_workflow_subject ON review_workflow(subject_type, subject_id);
CREATE INDEX idx_review_workflow_status ON review_workflow(status);

-- review_step
CREATE TABLE review_step (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    review_workflow_id UUID NOT NULL REFERENCES review_workflow(id),
    step_order INTEGER NOT NULL,
    reviewer_identity_id UUID NULL,
    reviewer_group_id UUID NULL,
    review_action_code VARCHAR(80) NULL,
    required BOOLEAN NOT NULL DEFAULT TRUE,
    status VARCHAR(40) NOT NULL DEFAULT 'pending',
    acted_at TIMESTAMPTZ NULL,
    rating_value NUMERIC(6,2) NULL,
    review_comment TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(review_workflow_id, step_order)
);

CREATE INDEX idx_review_step_workflow ON review_step(review_workflow_id);

-- review_record
CREATE TABLE review_record (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    review_workflow_id UUID NOT NULL REFERENCES review_workflow(id),
    review_step_id UUID NULL REFERENCES review_step(id),
    subject_type VARCHAR(80) NOT NULL,
    subject_id UUID NOT NULL,
    reviewer_identity_id UUID NULL,
    review_text TEXT NULL,
    rating_value NUMERIC(6,2) NULL,
    result_status VARCHAR(40) NOT NULL,
    schema_org_review_type VARCHAR(120) NULL,
    captured_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    review_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_review_record_workflow ON review_record(review_workflow_id);
CREATE INDEX idx_review_record_subject ON review_record(subject_type, subject_id);


-- ============================================
-- DELTA 2: WORKFLOW AND PROCESS TEMPLATE LAYER
-- ============================================

-- workflow_template
CREATE TABLE workflow_template (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NULL,
    template_type_id UUID NOT NULL REFERENCES master_template_type(id),
    template_code VARCHAR(80) NOT NULL,
    name VARCHAR(200) NOT NULL,
    process_family VARCHAR(80) NOT NULL,
    subject_type VARCHAR(80) NOT NULL,
    version_label VARCHAR(80) NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    is_system_template BOOLEAN NOT NULL DEFAULT FALSE,
    description TEXT NULL,
    template_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL,
    UNIQUE(tenant_id, template_code, version_label)
);

CREATE INDEX idx_workflow_template_tenant ON workflow_template(tenant_id);
CREATE INDEX idx_workflow_template_code ON workflow_template(template_code);

-- workflow_template_step
CREATE TABLE workflow_template_step (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_template_id UUID NOT NULL REFERENCES workflow_template(id),
    step_order INTEGER NOT NULL,
    step_code VARCHAR(80) NOT NULL,
    step_name VARCHAR(160) NOT NULL,
    step_kind VARCHAR(80) NOT NULL,
    subject_type VARCHAR(80) NULL,
    default_action_code VARCHAR(80) NULL,
    assignment_rule_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    entry_criteria_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    exit_criteria_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    sla_hours INTEGER NULL,
    is_required BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(workflow_template_id, step_order),
    UNIQUE(workflow_template_id, step_code)
);

CREATE INDEX idx_template_step_template ON workflow_template_step(workflow_template_id);

-- workflow_template_binding
CREATE TABLE workflow_template_binding (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    workflow_template_id UUID NOT NULL REFERENCES workflow_template(id),
    bound_subject_type VARCHAR(80) NOT NULL,
    bound_subject_subtype VARCHAR(80) NULL,
    content_type_id UUID NULL,
    document_type_id UUID NULL,
    partner_type VARCHAR(80) NULL,
    trigger_event_code VARCHAR(80) NULL,
    priority INTEGER NOT NULL DEFAULT 100,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_template_binding_template ON workflow_template_binding(workflow_template_id);

-- workflow_instance
CREATE TABLE workflow_instance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    workflow_template_id UUID NULL REFERENCES workflow_template(id),
    subject_type VARCHAR(80) NOT NULL,
    subject_id UUID NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'open',
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ NULL,
    owner_identity_id UUID NULL,
    instance_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL
);

CREATE INDEX idx_workflow_instance_tenant ON workflow_instance(tenant_id);
CREATE INDEX idx_workflow_instance_template ON workflow_instance(workflow_template_id);
CREATE INDEX idx_workflow_instance_subject ON workflow_instance(subject_type, subject_id);
CREATE INDEX idx_workflow_instance_status ON workflow_instance(status);

-- workflow_instance_step
CREATE TABLE workflow_instance_step (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_instance_id UUID NOT NULL REFERENCES workflow_instance(id),
    template_step_id UUID NULL REFERENCES workflow_template_step(id),
    step_order INTEGER NOT NULL,
    step_code VARCHAR(80) NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'pending',
    assigned_identity_id UUID NULL,
    assigned_group_id UUID NULL,
    opened_at TIMESTAMPTZ NULL,
    due_at TIMESTAMPTZ NULL,
    completed_at TIMESTAMPTZ NULL,
    result_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_instance_step_instance ON workflow_instance_step(workflow_instance_id);


-- ============================================
-- DELTA 3: ITSM ASSET CATALOGUE / CMDB / RESOURCE
-- ============================================

-- resource_master
CREATE TABLE resource_master (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    resource_type_id UUID NOT NULL REFERENCES master_resource_type(id),
    resource_code VARCHAR(80) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT NULL,
    owner_identity_id UUID NULL,
    manager_identity_id UUID NULL,
    cost_center VARCHAR(120) NULL,
    capacity_value NUMERIC(14,2) NULL,
    capacity_unit VARCHAR(40) NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'active',
    resource_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL,
    UNIQUE(tenant_id, resource_code)
);

CREATE INDEX idx_resource_master_tenant ON resource_master(tenant_id);
CREATE INDEX idx_resource_master_type ON resource_master(resource_type_id);

-- asset_catalog_item
CREATE TABLE asset_catalog_item (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NULL,
    asset_tag VARCHAR(120) NOT NULL,
    serial_number VARCHAR(160) NULL,
    asset_class VARCHAR(80) NOT NULL,
    vendor_name VARCHAR(160) NULL,
    model_name VARCHAR(160) NULL,
    purchase_date DATE NULL,
    warranty_end_date DATE NULL,
    assigned_identity_id UUID NULL,
    location_text VARCHAR(200) NULL,
    lifecycle_status VARCHAR(40) NOT NULL DEFAULT 'in_service',
    financial_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL,
    UNIQUE(tenant_id, asset_tag)
);

CREATE INDEX idx_asset_catalog_tenant ON asset_catalog_item(tenant_id);
CREATE INDEX idx_asset_catalog_tag ON asset_catalog_item(asset_tag);

-- configuration_item
CREATE TABLE configuration_item (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    resource_id UUID NULL REFERENCES resource_master(id),
    asset_catalog_item_id UUID NULL REFERENCES asset_catalog_item(id),
    ci_class VARCHAR(80) NOT NULL,
    ci_code VARCHAR(120) NOT NULL,
    name VARCHAR(200) NOT NULL,
    environment_code VARCHAR(40) NULL,
    operational_status VARCHAR(40) NOT NULL DEFAULT 'operational',
    lifecycle_stage VARCHAR(40) NULL,
    criticality VARCHAR(40) NULL,
    owner_identity_id UUID NULL,
    support_group_id UUID NULL,
    ci_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL,
    UNIQUE(tenant_id, ci_code)
);

CREATE INDEX idx_configuration_item_tenant ON configuration_item(tenant_id);
CREATE INDEX idx_configuration_item_code ON configuration_item(ci_code);

-- configuration_item_relationship
CREATE TABLE configuration_item_relationship (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    source_ci_id UUID NOT NULL REFERENCES configuration_item(id),
    target_ci_id UUID NOT NULL REFERENCES configuration_item(id),
    relationship_type VARCHAR(80) NOT NULL,
    directionality VARCHAR(40) NULL,
    is_critical_path BOOLEAN NOT NULL DEFAULT FALSE,
    effective_from TIMESTAMPTZ NULL,
    effective_to TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(source_ci_id, target_ci_id, relationship_type, effective_from)
);

CREATE INDEX idx_ci_rel_source ON configuration_item_relationship(source_ci_id);
CREATE INDEX idx_ci_rel_target ON configuration_item_relationship(target_ci_id);

-- service_catalog_item
CREATE TABLE service_catalog_item (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    catalog_code VARCHAR(80) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT NULL,
    business_service_ci_id UUID NULL REFERENCES configuration_item(id),
    service_offering_ci_id UUID NULL REFERENCES configuration_item(id),
    request_workflow_template_id UUID NULL,
    approval_workflow_template_id UUID NULL,
    is_requestable BOOLEAN NOT NULL DEFAULT TRUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL,
    UNIQUE(tenant_id, catalog_code)
);

CREATE INDEX idx_service_catalog_tenant ON service_catalog_item(tenant_id);

-- service_request
CREATE TABLE service_request (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    catalog_item_id UUID NOT NULL REFERENCES service_catalog_item(id),
    requested_by_identity_id UUID NOT NULL,
    beneficiary_identity_id UUID NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'open',
    urgency VARCHAR(40) NULL,
    impact VARCHAR(40) NULL,
    request_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    opened_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_service_request_tenant ON service_request(tenant_id);
CREATE INDEX idx_service_request_catalog ON service_request(catalog_item_id);
CREATE INDEX idx_service_request_status ON service_request(status);


-- ============================================
-- DELTA 4: ENTERPRISE PROCESS PACKS
-- ============================================

-- master_process_family
CREATE TABLE master_process_family (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(80) UNIQUE NOT NULL,
    name VARCHAR(160) NOT NULL,
    description TEXT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL
);

-- master_process_type
CREATE TABLE master_process_type (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    process_family_id UUID NOT NULL REFERENCES master_process_family(id),
    code VARCHAR(80) UNIQUE NOT NULL,
    name VARCHAR(160) NOT NULL,
    subject_type VARCHAR(80) NOT NULL,
    default_template_id UUID NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL
);

CREATE INDEX idx_master_process_type_code ON master_process_type(code);
CREATE INDEX idx_master_process_family ON master_process_type(process_family_id);

-- process_case
CREATE TABLE process_case (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    process_type_id UUID NOT NULL REFERENCES master_process_type(id),
    workflow_instance_id UUID NULL REFERENCES workflow_instance(id),
    subject_type VARCHAR(80) NOT NULL,
    subject_id UUID NOT NULL,
    case_code VARCHAR(120) NULL,
    title VARCHAR(240) NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'open',
    owner_identity_id UUID NULL,
    opened_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at TIMESTAMPTZ NULL,
    case_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL
);

CREATE INDEX idx_process_case_tenant ON process_case(tenant_id);
CREATE INDEX idx_process_case_type ON process_case(process_type_id);
CREATE INDEX idx_process_case_subject ON process_case(subject_type, subject_id);
CREATE INDEX idx_process_case_status ON process_case(status);


-- ============================================
-- DELTA 5: HIRING WORKFLOW SUPPORT
-- ============================================

-- job_requisition
CREATE TABLE job_requisition (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    project_id UUID NULL,
    department_id UUID NULL,
    job_title_id UUID NULL,
    requisition_code VARCHAR(120) NOT NULL,
    title VARCHAR(200) NOT NULL,
    hiring_manager_employee_id UUID NULL,
    recruiter_identity_id UUID NULL,
    headcount_requested INTEGER NOT NULL DEFAULT 1,
    employment_type VARCHAR(80) NULL,
    location_text VARCHAR(160) NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    opened_at TIMESTAMPTZ NULL,
    closed_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL,
    UNIQUE(tenant_id, requisition_code)
);

CREATE INDEX idx_job_requisition_tenant ON job_requisition(tenant_id);
CREATE INDEX idx_job_requisition_status ON job_requisition(status);

-- candidate_profile
CREATE TABLE candidate_profile (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    identity_id UUID NULL,
    candidate_code VARCHAR(120) NULL,
    full_name VARCHAR(200) NOT NULL,
    primary_email VARCHAR(200) NULL,
    phone VARCHAR(50) NULL,
    source_channel VARCHAR(80) NULL,
    resume_file_asset_id UUID NULL,
    profile_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL
);

CREATE INDEX idx_candidate_profile_tenant ON candidate_profile(tenant_id);
CREATE INDEX idx_candidate_profile_code ON candidate_profile(candidate_code);

-- candidate_application
CREATE TABLE candidate_application (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    job_requisition_id UUID NOT NULL REFERENCES job_requisition(id),
    candidate_profile_id UUID NOT NULL REFERENCES candidate_profile(id),
    application_status VARCHAR(40) NOT NULL DEFAULT 'applied',
    applied_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    current_stage_code VARCHAR(80) NULL,
    assigned_recruiter_identity_id UUID NULL,
    rating_value NUMERIC(6,2) NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_candidate_application_requisition ON candidate_application(job_requisition_id);
CREATE INDEX idx_candidate_application_candidate ON candidate_application(candidate_profile_id);
CREATE INDEX idx_candidate_application_status ON candidate_application(application_status);

-- candidate_interview
CREATE TABLE candidate_interview (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    candidate_application_id UUID NOT NULL REFERENCES candidate_application(id),
    interview_type VARCHAR(80) NOT NULL,
    scheduled_at TIMESTAMPTZ NULL,
    interviewer_identity_id UUID NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'scheduled',
    feedback_text TEXT NULL,
    rating_value NUMERIC(6,2) NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_candidate_interview_application ON candidate_interview(candidate_application_id);
CREATE INDEX idx_candidate_interview_status ON candidate_interview(status);


-- ============================================
-- DELTA 6: CHURN-REDUCTION WORKFLOW SUPPORT
-- ============================================

-- customer_account
CREATE TABLE customer_account (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    partner_account_id UUID NULL,
    account_code VARCHAR(120) NOT NULL,
    name VARCHAR(200) NOT NULL,
    owner_identity_id UUID NULL,
    customer_status VARCHAR(40) NOT NULL DEFAULT 'active',
    health_score NUMERIC(6,2) NULL,
    renewal_date DATE NULL,
    arr_value NUMERIC(14,2) NULL,
    risk_tier VARCHAR(40) NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL,
    UNIQUE(tenant_id, account_code)
);

CREATE INDEX idx_customer_account_tenant ON customer_account(tenant_id);
CREATE INDEX idx_customer_account_partner ON customer_account(partner_account_id);
CREATE INDEX idx_customer_account_status ON customer_account(customer_status);

-- customer_signal
CREATE TABLE customer_signal (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    customer_account_id UUID NOT NULL REFERENCES customer_account(id),
    signal_type VARCHAR(80) NOT NULL,
    signal_score NUMERIC(6,2) NULL,
    signal_source VARCHAR(120) NULL,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    signal_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_customer_signal_account ON customer_signal(customer_account_id);
CREATE INDEX idx_customer_signal_type ON customer_signal(signal_type);
CREATE INDEX idx_customer_signal_observed ON customer_signal(observed_at);

-- retention_playbook_run
CREATE TABLE retention_playbook_run (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    customer_account_id UUID NOT NULL REFERENCES customer_account(id),
    workflow_instance_id UUID NULL REFERENCES workflow_instance(id),
    playbook_code VARCHAR(80) NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'open',
    triggered_by_signal_id UUID NULL,
    owner_identity_id UUID NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ NULL,
    run_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_retention_playbook_account ON retention_playbook_run(customer_account_id);
CREATE INDEX idx_retention_playbook_status ON retention_playbook_run(status);


-- ============================================
-- UPDATE U1: approval - Add content/workflow/process refs
-- ============================================

ALTER TABLE approval 
    ADD COLUMN IF NOT EXISTS content_item_id UUID NULL REFERENCES content_item(id),
    ADD COLUMN IF NOT EXISTS workflow_instance_id UUID NULL REFERENCES workflow_instance(id),
    ADD COLUMN IF NOT EXISTS process_case_id UUID NULL REFERENCES process_case(id);

CREATE INDEX IF NOT EXISTS idx_approval_content ON approval(content_item_id);
CREATE INDEX IF NOT EXISTS idx_approval_workflow ON approval(workflow_instance_id);
CREATE INDEX IF NOT EXISTS idx_approval_process ON approval(process_case_id);


-- ============================================
-- UPDATE U2: task - Add workflow/process/action/content refs
-- ============================================

ALTER TABLE task 
    ADD COLUMN IF NOT EXISTS workflow_instance_id UUID NULL REFERENCES workflow_instance(id),
    ADD COLUMN IF NOT EXISTS workflow_instance_step_id UUID NULL,
    ADD COLUMN IF NOT EXISTS process_case_id UUID NULL REFERENCES process_case(id),
    ADD COLUMN IF NOT EXISTS action_code VARCHAR(80) NULL,
    ADD COLUMN IF NOT EXISTS content_item_id UUID NULL REFERENCES content_item(id);

CREATE INDEX IF NOT EXISTS idx_task_workflow ON task(workflow_instance_id);
CREATE INDEX IF NOT EXISTS idx_task_process ON task(process_case_id);
CREATE INDEX IF NOT EXISTS idx_task_action ON task(action_code);
CREATE INDEX IF NOT EXISTS idx_task_content ON task(content_item_id);


-- ============================================
-- UPDATE U3: decision - Add process/review/content refs
-- ============================================

ALTER TABLE decision 
    ADD COLUMN IF NOT EXISTS process_case_id UUID NULL REFERENCES process_case(id),
    ADD COLUMN IF NOT EXISTS content_item_id UUID NULL REFERENCES content_item(id),
    ADD COLUMN IF NOT EXISTS review_workflow_id UUID NULL REFERENCES review_workflow(id);

CREATE INDEX IF NOT EXISTS idx_decision_process ON decision(process_case_id);
CREATE INDEX IF NOT EXISTS idx_decision_content ON decision(content_item_id);
CREATE INDEX IF NOT EXISTS idx_decision_review ON decision(review_workflow_id);


-- ============================================
-- UPDATE U4: file_asset - Add document/content/template refs
-- ============================================

ALTER TABLE file_asset 
    ADD COLUMN IF NOT EXISTS document_type_id UUID NULL REFERENCES master_document_type(id),
    ADD COLUMN IF NOT EXISTS content_item_id UUID NULL REFERENCES content_item(id),
    ADD COLUMN IF NOT EXISTS source_template_id UUID NULL;

CREATE INDEX IF NOT EXISTS idx_file_asset_document ON file_asset(document_type_id);
CREATE INDEX IF NOT EXISTS idx_file_asset_content ON file_asset(content_item_id);


-- ============================================
-- UPDATE U5: message_event - Add action/process refs
-- ============================================

ALTER TABLE message_event 
    ADD COLUMN IF NOT EXISTS action_code VARCHAR(80) NULL,
    ADD COLUMN IF NOT EXISTS process_case_id UUID NULL REFERENCES process_case(id);

CREATE INDEX IF NOT EXISTS idx_message_action ON message_event(action_code);
CREATE INDEX IF NOT EXISTS idx_message_process ON message_event(process_case_id);


-- ============================================
-- UPDATE U6: partner_account - Add tier/stage/review refs
-- ============================================

ALTER TABLE partner_account 
    ADD COLUMN IF NOT EXISTS partner_tier VARCHAR(40) NULL,
    ADD COLUMN IF NOT EXISTS relationship_stage VARCHAR(40) NULL,
    ADD COLUMN IF NOT EXISTS default_review_template_id UUID NULL;

CREATE INDEX IF NOT EXISTS idx_partner_tier ON partner_account(partner_tier);
CREATE INDEX IF NOT EXISTS idx_partner_stage ON partner_account(relationship_stage);


-- ============================================
-- UPDATE U8: master_channel - Add schema_org_type
-- ============================================

ALTER TABLE master_channel 
    ADD COLUMN IF NOT EXISTS schema_org_type VARCHAR(120) NULL;


-- ============================================
-- ENUMERATION CONSTRAINTS FOR NEW TABLES
-- ============================================

-- content_item creative_work_status check
ALTER TABLE content_item 
    ADD CONSTRAINT chk_content_work_status 
    CHECK (creative_work_status IN ('draft', 'review', 'approved', 'published', 'archived', 'withdrawn'));

-- content_version status check
ALTER TABLE content_version 
    ADD CONSTRAINT chk_content_version_status 
    CHECK (status IN ('draft', 'pending_review', 'approved', 'published', 'superseded'));

-- review_workflow status check
ALTER TABLE review_workflow 
    ADD CONSTRAINT chk_review_status 
    CHECK (status IN ('open', 'in_review', 'completed', 'cancelled'));

-- review_step status check
ALTER TABLE review_step 
    ADD CONSTRAINT chk_review_step_status 
    CHECK (status IN ('pending', 'approved', 'rejected', 'skipped'));

-- review_record result_status check
ALTER TABLE review_record 
    ADD CONSTRAINT chk_review_record_status 
    CHECK (result_status IN ('approved', 'rejected', 'conditional', 'pending'));

-- workflow_template status check
ALTER TABLE workflow_template 
    ADD CONSTRAINT chk_template_status 
    CHECK (status IN ('draft', 'active', 'deprecated', 'archived'));

-- workflow_instance status check
ALTER TABLE workflow_instance 
    ADD CONSTRAINT chk_instance_status 
    CHECK (status IN ('open', 'in_progress', 'completed', 'cancelled', 'on_hold'));

-- workflow_instance_step status check
ALTER TABLE workflow_instance_step 
    ADD CONSTRAINT chk_instance_step_status 
    CHECK (status IN ('pending', 'in_progress', 'completed', 'skipped', 'failed')).

-- configuration_item operational_status check
ALTER TABLE configuration_item 
    ADD CONSTRAINT chk_ci_operational_status 
    CHECK (operational_status IN ('operational', 'degraded', 'down', 'maintenance', 'discovered'));

-- configuration_item lifecycle_stage check
ALTER TABLE configuration_item 
    ADD CONSTRAINT chk_ci_lifecycle_stage 
    CHECK (lifecycle_stage IN ('planning', 'building', 'testing', 'production', 'retired'));

-- asset_catalog_item lifecycle_status check
ALTER TABLE asset_catalog_item 
    ADD CONSTRAINT chk_asset_lifecycle 
    CHECK (lifecycle_status IN ('in_service', 'spare', 'repair', 'retired', 'disposed'));

-- service_request status check
ALTER TABLE service_request 
    ADD CONSTRAINT chk_service_request_status 
    CHECK (status IN ('open', 'pending_approval', 'in_progress', 'resolved', 'closed', 'cancelled'));

-- process_case status check
ALTER TABLE process_case 
    ADD CONSTRAINT chk_process_case_status 
    CHECK (status IN ('open', 'in_progress', 'completed', 'cancelled', 'on_hold'));

-- job_requisition status check
ALTER TABLE job_requisition 
    ADD CONSTRAINT chk_job_requisition_status 
    CHECK (status IN ('draft', 'open', 'filled', 'cancelled', 'on_hold'));

-- candidate_application status check
ALTER TABLE candidate_application 
    ADD CONSTRAINT chk_application_status 
    CHECK (application_status IN ('applied', 'screening', 'interview', 'offer', 'hired', 'rejected', 'withdrawn'));

-- candidate_interview status check
ALTER TABLE candidate_interview 
    ADD CONSTRAINT chk_interview_status 
    CHECK (status IN ('scheduled', 'completed', 'no_show', 'cancelled'));

-- customer_account customer_status check
ALTER TABLE customer_account 
    ADD CONSTRAINT chk_customer_status 
    CHECK (customer_status IN ('active', 'churned', 'suspended', 'at_risk'));

-- retention_playbook_run status check
ALTER TABLE retention_playbook_run 
    ADD CONSTRAINT chk_playbook_status 
    CHECK (status IN ('open', 'in_progress', 'completed', 'failed'));


-- ============================================
-- DELTA COMPLETION METADATA
-- ============================================
-- Delta version: v1
-- New tables added: 31
-- Updated tables: 7
-- Total tables after delta: 76 + 31 = 107
-- Generated: 2026-04-20
-- ============================================