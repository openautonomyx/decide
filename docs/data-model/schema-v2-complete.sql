-- Autonomyx Decide Schema v2 - Complete Enterprise DDL
-- 
-- This is a comprehensive reconstruction based on the architecture checkpoint
-- preserving all 76 tables across 12 functional families.
--
-- Design principles (from architecture):
-- 1. Human employee and agent are never merged
-- 2. Product, project, and group remain distinct
-- 3. Workflow entities remain explicit: task, milestone, reminder, escalation
-- 4. Decision/control-plane entities remain explicit
-- 5. Memory/state remains explicit in 9 layers
-- 6. Auth can project into IAM but domain truth stays in tables
-- 7. JSONB used sparingly (evidence, metadata, config only)
--
-- NOTE: [R] = Reconstructed from architecture inference
--       [O] = Original from recovered artifacts
-- ============================================

-- ============================================
-- COMMON EXTENSIONS & TYPES
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- COMMON CONVENTIONS MACRO (as comments for reference)
-- ============================================
-- These columns appear on almost every mutable table:
--   id UUID PRIMARY KEY DEFAULT uuid_generate_v4()
--   created_at TIMESTAMPTZ NOT NULL DEFAULT now()
--   updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
--   created_by_identity_id UUID NULL
--   updated_by_identity_id UUID NULL
--   row_version INTEGER NOT NULL DEFAULT 1
--   is_deleted BOOLEAN NOT NULL DEFAULT FALSE
--   deleted_at TIMESTAMPTZ NULL

-- ============================================
-- TABLE FAMILY 1: MASTER DATA / REFERENCE TABLES
-- ============================================

-- 1. master_country [O - original structure]
CREATE TABLE master_country (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    iso2_code VARCHAR(2) UNIQUE NOT NULL,
    iso3_code VARCHAR(3) UNIQUE NOT NULL,
    name VARCHAR(120) NOT NULL,
    phone_code VARCHAR(10) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL
);

CREATE INDEX idx_master_country_iso2 ON master_country(iso2_code);
CREATE INDEX idx_master_country_iso3 ON master_country(iso3_code);

-- 2. master_region [O]
CREATE TABLE master_region (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    country_id UUID NOT NULL REFERENCES master_country(id),
    code VARCHAR(20) NOT NULL,
    name VARCHAR(120) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL,
    UNIQUE(country_id, code)
);

CREATE INDEX idx_master_region_country ON master_region(country_id);

-- 3. master_department [O]
CREATE TABLE master_department (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NULL,
    code VARCHAR(50) NOT NULL,
    name VARCHAR(120) NOT NULL,
    description TEXT NULL,
    parent_department_id UUID NULL REFERENCES master_department(id),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL,
    UNIQUE(tenant_id, code)
);

CREATE INDEX idx_master_department_tenant ON master_department(tenant_id);
CREATE INDEX idx_master_department_parent ON master_department(parent_department_id);

-- 4. master_job_title [O]
CREATE TABLE master_job_title (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NULL,
    code VARCHAR(50) NOT NULL,
    name VARCHAR(120) NOT NULL,
    job_family VARCHAR(120) NULL,
    level_code VARCHAR(50) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL,
    UNIQUE(tenant_id, code)
);

CREATE INDEX idx_master_job_title_tenant ON master_job_title(tenant_id);
CREATE INDEX idx_master_job_title_family ON master_job_title(job_family);

-- 5. master_skill [O]
CREATE TABLE master_skill (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(80) UNIQUE NOT NULL,
    name VARCHAR(160) NOT NULL,
    category VARCHAR(120) NULL,
    framework_name VARCHAR(120) NULL,
    description TEXT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL
);

CREATE INDEX idx_master_skill_code ON master_skill(code);
CREATE INDEX idx_master_skill_category ON master_skill(category);

-- 6. master_certification [O]
CREATE TABLE master_certification (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(80) UNIQUE NOT NULL,
    name VARCHAR(160) NOT NULL,
    issuing_authority VARCHAR(160) NULL,
    description TEXT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL
);

CREATE INDEX idx_master_certification_code ON master_certification(code);

-- 7. master_topic [O]
CREATE TABLE master_topic (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(80) UNIQUE NOT NULL,
    name VARCHAR(160) NOT NULL,
    description TEXT NULL,
    parent_topic_id UUID NULL REFERENCES master_topic(id),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL
);

CREATE INDEX idx_master_topic_code ON master_topic(code);
CREATE INDEX idx_master_topic_parent ON master_topic(parent_topic_id);

-- 8. master_channel [O]
CREATE TABLE master_channel (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(80) UNIQUE NOT NULL,
    channel_type VARCHAR(40) NOT NULL,
    name VARCHAR(120) NOT NULL,
    description TEXT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL
);

-- 9. master_policy_type [O]
CREATE TABLE master_policy_type (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(80) UNIQUE NOT NULL,
    name VARCHAR(160) NOT NULL,
    description TEXT NULL,
    effect_scope VARCHAR(80) NULL, -- [R]
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL
);

-- 10. master_memory_profile_template [O]
CREATE TABLE master_memory_profile_template (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(80) UNIQUE NOT NULL,
    name VARCHAR(160) NOT NULL,
    description TEXT NULL,
    default_config JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL
);


-- ============================================
-- TABLE FAMILY 2: TENANT / ORGANIZATION / PARTNER DOMAIN
-- ============================================

-- 11. tenant [O]
CREATE TABLE tenant (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(80) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(120) UNIQUE NOT NULL,
    organization_type VARCHAR(40) NOT NULL DEFAULT 'tenant',
    status VARCHAR(40) NOT NULL DEFAULT 'active', -- [R]
    primary_domain VARCHAR(200) NULL,
    billing_email VARCHAR(200) NULL,
    country_id UUID NULL REFERENCES master_country(id),
    region_id UUID NULL REFERENCES master_region(id),
    timezone VARCHAR(80) NULL,
    data_residency_region VARCHAR(80) NULL,
    plan_code VARCHAR(80) NULL,
    effective_from TIMESTAMPTZ NULL,
    effective_to TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL
);

CREATE INDEX idx_tenant_code ON tenant(code);
CREATE INDEX idx_tenant_slug ON tenant(slug);

-- 12. tenant_settings [R]
CREATE TABLE tenant_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID UNIQUE NOT NULL REFERENCES tenant(id),
    locale VARCHAR(20) NULL,
    default_currency VARCHAR(10) NULL,
    default_channel_id UUID NULL REFERENCES master_channel(id),
    auth_mode VARCHAR(80) NULL, -- [R]
    require_mfa BOOLEAN NOT NULL DEFAULT FALSE,
    allow_external_collaborators BOOLEAN NOT NULL DEFAULT FALSE,
    retention_policy_days INTEGER NULL,
    settings_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 13. partner_account [R]
CREATE TABLE partner_account (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    code VARCHAR(80) NOT NULL,
    name VARCHAR(200) NOT NULL,
    partner_type VARCHAR(80) NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'active', -- [R]
    external_account_ref VARCHAR(160) NULL,
    website_url TEXT NULL,
    primary_contact_email VARCHAR(200) NULL,
    country_id UUID NULL REFERENCES master_country(id),
    timezone VARCHAR(80) NULL,
    notes TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL,
    UNIQUE(tenant_id, code)
);

CREATE INDEX idx_partner_account_tenant ON partner_account(tenant_id);

-- 14. partner_account_sponsor [R]
CREATE TABLE partner_account_sponsor (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    partner_account_id UUID NOT NULL REFERENCES partner_account(id),
    sponsor_identity_id UUID NOT NULL,
    sponsor_role VARCHAR(80) NOT NULL,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    start_at TIMESTAMPTZ NULL,
    end_at TIMESTAMPTZ NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'active', -- [R]
    sponsor_notes TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_partner_sponsor_account ON partner_account_sponsor(partner_account_id);

-- 15. organization_membership [R]
CREATE TABLE organization_membership (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    identity_id UUID NOT NULL,
    organization_kind VARCHAR(40) NOT NULL,
    organization_id UUID NOT NULL,
    membership_role VARCHAR(80) NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'active', -- [R]
    joined_at TIMESTAMPTZ NULL,
    left_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(identity_id, organization_kind, organization_id, membership_role)
);

CREATE INDEX idx_org_membership_identity ON organization_membership(identity_id);


-- ============================================
-- TABLE FAMILY 3: IDENTITY DOMAIN
-- ============================================

-- 16. identity [O]
CREATE TABLE identity (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NULL REFERENCES tenant(id),
    identity_type VARCHAR(40) NOT NULL, -- human|agent|service|partner_user|external_system
    display_name VARCHAR(200) NOT NULL,
    external_key VARCHAR(200) NULL,
    username VARCHAR(160) NULL,
    email VARCHAR(200) NULL,
    phone VARCHAR(50) NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'active',
    keycloak_realm_id VARCHAR(120) NULL,
    keycloak_user_id VARCHAR(120) NULL,
    keycloak_client_id VARCHAR(120) NULL,
    service_account_user_id VARCHAR(120) NULL,
    is_system BOOLEAN NOT NULL DEFAULT FALSE,
    last_seen_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL,
    UNIQUE(tenant_id, username),
    UNIQUE(tenant_id, email)
);

CREATE INDEX idx_identity_tenant_type ON identity(tenant_id, identity_type);
CREATE INDEX idx_identity_tenant_status ON identity(tenant_id, status);
CREATE INDEX idx_identity_type ON identity(identity_type);

-- 17. identity_attribute [O]
CREATE TABLE identity_attribute (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    identity_id UUID NOT NULL REFERENCES identity(id),
    attribute_name VARCHAR(120) NOT NULL,
    attribute_value TEXT NULL,
    attribute_json JSONB NULL,
    is_sensitive BOOLEAN NOT NULL DEFAULT FALSE,
    source_system VARCHAR(120) NULL,
    effective_from TIMESTAMPTZ NULL,
    effective_to TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(identity_id, attribute_name, effective_from)
);

CREATE INDEX idx_identity_attr_identity ON identity_attribute(identity_id);

-- 18. identity_lifecycle_state [R]
CREATE TABLE identity_lifecycle_state (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    identity_id UUID NOT NULL REFERENCES identity(id),
    state_code VARCHAR(80) NOT NULL,
    state_reason TEXT NULL,
    entered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    exited_at TIMESTAMPTZ NULL,
    entered_by_identity_id UUID NULL,
    approval_id UUID NULL,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_lifecycle_identity ON identity_lifecycle_state(identity_id);
CREATE INDEX idx_lifecycle_current ON identity_lifecycle_state(identity_id, is_current);

-- 19. identity_auth_projection [R]
CREATE TABLE identity_auth_projection (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    identity_id UUID UNIQUE NOT NULL REFERENCES identity(id),
    auth_status VARCHAR(40) NOT NULL,
    login_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    mfa_required BOOLEAN NOT NULL DEFAULT FALSE,
    passwordless_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    scim_managed BOOLEAN NOT NULL DEFAULT FALSE,
    sso_only BOOLEAN NOT NULL DEFAULT FALSE,
    auth_projection_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);


-- ============================================
-- TABLE FAMILY 4: EMPLOYEE DOMAIN
-- ============================================

-- 20. employee [O]
CREATE TABLE employee (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    identity_id UUID UNIQUE NOT NULL REFERENCES identity(id),
    employee_number VARCHAR(80) NULL,
    department_id UUID NULL REFERENCES master_department(id),
    job_title_id UUID NULL REFERENCES master_job_title(id),
    manager_employee_id UUID NULL REFERENCES employee(id),
    employment_type VARCHAR(80) NULL,
    employment_status VARCHAR(40) NOT NULL DEFAULT 'active',
    hire_date DATE NULL,
    end_date DATE NULL,
    work_location VARCHAR(160) NULL,
    cost_center VARCHAR(120) NULL,
    is_people_manager BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL,
    UNIQUE(tenant_id, employee_number)
);

CREATE INDEX idx_employee_tenant ON employee(tenant_id);
CREATE INDEX idx_employee_department ON employee(department_id);
CREATE INDEX idx_employee_status ON employee(employment_status);
CREATE INDEX idx_employee_identity ON employee(identity_id);

-- 21. employee_profile [O]
CREATE TABLE employee_profile (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID UNIQUE NOT NULL REFERENCES employee(id),
    first_name VARCHAR(120) NOT NULL,
    middle_name VARCHAR(120) NULL,
    last_name VARCHAR(120) NULL,
    preferred_name VARCHAR(120) NULL,
    legal_name VARCHAR(240) NULL,
--  [R] Fields inferred from employment lifecycle needs
    birth_date DATE NULL,
    pronouns VARCHAR(80) NULL,
    bio TEXT NULL,
    profile_photo_url TEXT NULL,
    locale VARCHAR(20) NULL,
    timezone VARCHAR(80) NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 22. employee_skill [O]
CREATE TABLE employee_skill (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID NOT NULL REFERENCES employee(id),
    skill_id UUID NOT NULL REFERENCES master_skill(id),
    proficiency_level VARCHAR(40) NULL,
    years_experience NUMERIC(5,2) NULL,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    source VARCHAR(80) NULL,
    verified_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL,
    UNIQUE(employee_id, skill_id)
);

CREATE INDEX idx_employee_skill_employee ON employee_skill(employee_id);

-- 23. employee_certification [O]
CREATE TABLE employee_certification (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID NOT NULL REFERENCES employee(id),
    certification_id UUID NOT NULL REFERENCES master_certification(id),
    certificate_number VARCHAR(120) NULL,
    issued_at DATE NULL,
    expires_at DATE NULL,
    issuing_authority VARCHAR(160) NULL,
    verification_url TEXT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'active', -- [R]
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_employee_cert_employee ON employee_certification(employee_id);

-- 24. employee_education [O]
CREATE TABLE employee_education (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID NOT NULL REFERENCES employee(id),
    institution_name VARCHAR(200) NOT NULL,
    degree_name VARCHAR(200) NULL,
    field_of_study VARCHAR(200) NULL,
    start_date DATE NULL,
    end_date DATE NULL,
    grade_text VARCHAR(80) NULL,
    notes TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 25. employee_employment_history [O]
CREATE TABLE employee_employment_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID NOT NULL REFERENCES employee(id),
    organization_name VARCHAR(200) NOT NULL,
    job_title_text VARCHAR(200) NULL,
    start_date DATE NULL,
    end_date DATE NULL,
    employment_type VARCHAR(80) NULL,
    description TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 26. employee_group_membership [O]
CREATE TABLE employee_group_membership (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    employee_id UUID NOT NULL REFERENCES employee(id),
    group_id UUID NOT NULL,
    membership_role VARCHAR(80) NULL,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    joined_at TIMESTAMPTZ NULL,
    left_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(employee_id, group_id)
);

CREATE INDEX idx_emp_group_employee ON employee_group_membership(employee_id);
CREATE INDEX idx_emp_group_group ON employee_group_membership(group_id);


-- ============================================
-- TABLE FAMILY 5: AGENT DOMAIN
-- ============================================

-- 27. agent [O]
CREATE TABLE agent (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    identity_id UUID UNIQUE NOT NULL REFERENCES identity(id),
    agent_code VARCHAR(80) NOT NULL,
    name VARCHAR(200) NOT NULL,
    agent_type VARCHAR(80) NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'requested',
    primary_owner_employee_id UUID NULL REFERENCES employee(id),
    supervisor_employee_id UUID NULL REFERENCES employee(id),
    parent_agent_id UUID NULL REFERENCES agent(id),
    sponsor_identity_id UUID NULL,
    runtime_type VARCHAR(80) NULL,
    default_channel_id UUID NULL REFERENCES master_channel(id),
    active_from TIMESTAMPTZ NULL,
    active_to TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL,
    UNIQUE(tenant_id, agent_code)
);

CREATE INDEX idx_agent_tenant ON agent(tenant_id);
CREATE INDEX idx_agent_type ON agent(agent_type);
CREATE INDEX idx_agent_status ON agent(status);
CREATE INDEX idx_agent_identity ON agent(identity_id);

-- 28. agent_profile [O]
CREATE TABLE agent_profile (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID UNIQUE NOT NULL REFERENCES agent(id),
    purpose TEXT NOT NULL,
    persona_summary TEXT NULL,
    system_prompt_ref TEXT NULL, -- [R]
    objective_text TEXT NULL,
    default_language VARCHAR(20) NULL,
    autonomy_level VARCHAR(40) NULL,
    response_style VARCHAR(80) NULL,
    profile_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 29. agent_goal [O]
CREATE TABLE agent_goal (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agent(id),
    goal_title VARCHAR(200) NOT NULL,
    goal_description TEXT NULL,
    priority INTEGER NOT NULL DEFAULT 3,
    status VARCHAR(40) NOT NULL DEFAULT 'active', -- [R]
    target_date TIMESTAMPTZ NULL,
    achieved_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_agent_goal_agent ON agent_goal(agent_id);

-- 30. agent_skill_profile [O]
CREATE TABLE agent_skill_profile (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agent(id),
    skill_id UUID NOT NULL REFERENCES master_skill(id),
    proficiency_level VARCHAR(40) NULL,
    source_type VARCHAR(80) NULL,
    inherited_from_employee_id UUID NULL,
    confidence_score NUMERIC(5,2) NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(agent_id, skill_id)
);

CREATE INDEX idx_agent_skill_agent ON agent_skill_profile(agent_id);

-- 31. agent_preference [O]
CREATE TABLE agent_preference (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agent(id),
    preference_key VARCHAR(120) NOT NULL,
    preference_value TEXT NULL,
    preference_json JSONB NULL,
    source VARCHAR(80) NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(agent_id, preference_key)
);

-- 32. agent_constraint [O]
CREATE TABLE agent_constraint (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agent(id),
    constraint_type VARCHAR(80) NOT NULL,
    constraint_code VARCHAR(80) NULL,
    description TEXT NOT NULL,
    hard_limit BOOLEAN NOT NULL DEFAULT TRUE,
    constraint_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    effective_from TIMESTAMPTZ NULL,
    effective_to TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_agent_constraint_agent ON agent_constraint(agent_id);

-- 33. agent_memory_profile [O]
CREATE TABLE agent_memory_profile (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID UNIQUE NOT NULL REFERENCES agent(id),
    profile_template_id UUID NULL REFERENCES master_memory_profile_template(id),
    working_ttl_seconds INTEGER NULL,
    episodic_retention_days INTEGER NULL,
    semantic_retention_days INTEGER NULL,
    cortex_refresh_minutes INTEGER NULL,
    vector_namespace VARCHAR(160) NULL,
    checkpoint_frequency_minutes INTEGER NULL,
    audit_retention_days INTEGER NULL,
    config_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 34. agent_governance_profile [O]
CREATE TABLE agent_governance_profile (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID UNIQUE NOT NULL REFERENCES agent(id),
    approval_required BOOLEAN NOT NULL DEFAULT FALSE,
    max_autonomous_actions INTEGER NULL,
    max_cost_per_run NUMERIC(12,2) NULL,
    max_cost_per_day NUMERIC(12,2) NULL,
    escalation_policy_id UUID NULL,
    policy_bundle_id UUID NULL,
    requires_human_sponsor BOOLEAN NOT NULL DEFAULT TRUE,
    governance_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 35. agent_group_membership [O]
CREATE TABLE agent_group_membership (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    agent_id UUID NOT NULL REFERENCES agent(id),
    group_id UUID NOT NULL,
    membership_role VARCHAR(80) NULL,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    joined_at TIMESTAMPTZ NULL,
    left_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(agent_id, group_id)
);

CREATE INDEX idx_agent_group_agent ON agent_group_membership(agent_id);
CREATE INDEX idx_agent_group_group ON agent_group_membership(group_id);

-- 36. agent_identity_credential_ref [R]
CREATE TABLE agent_identity_credential_ref (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agent(id),
    credential_type VARCHAR(80) NOT NULL,
    secret_ref VARCHAR(240) NOT NULL,
    key_id VARCHAR(160) NULL,
    provider_name VARCHAR(120) NULL,
    issued_at TIMESTAMPTZ NULL,
    expires_at TIMESTAMPTZ NULL,
    rotation_due_at TIMESTAMPTZ NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'active', -- [R]
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_agent_credential_agent ON agent_identity_credential_ref(agent_id);


-- ============================================
-- TABLE FAMILY 6: EMPLOYEE-AGENT RELATIONSHIP DOMAIN
-- ============================================

-- 37. employee_agent_assignment [O]
CREATE TABLE employee_agent_assignment (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    employee_id UUID NOT NULL REFERENCES employee(id),
    agent_id UUID NOT NULL REFERENCES agent(id),
    assignment_type VARCHAR(40) NOT NULL,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    start_date DATE NULL,
    end_date DATE NULL,
    assignment_notes TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(employee_id, agent_id, assignment_type, start_date)
);

CREATE INDEX idx_emp_assign_employee ON employee_agent_assignment(employee_id);
CREATE INDEX idx_emp_assign_agent ON employee_agent_assignment(agent_id);

-- 38. employee_agent_supervision [R]
CREATE TABLE employee_agent_supervision (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    supervisor_employee_id UUID NOT NULL REFERENCES employee(id),
    agent_id UUID NOT NULL REFERENCES agent(id),
    supervision_scope VARCHAR(80) NULL,
    start_at TIMESTAMPTZ NULL,
    end_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(supervisor_employee_id, agent_id, start_at)
);

CREATE INDEX idx_supervision_supervisor ON employee_agent_supervision(supervisor_employee_id);
CREATE INDEX idx_supervision_agent ON employee_agent_supervision(agent_id);

-- 39. employee_agent_goal_link [R]
CREATE TABLE employee_agent_goal_link (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    employee_id UUID NOT NULL REFERENCES employee(id),
    agent_goal_id UUID NOT NULL REFERENCES agent_goal(id),
    relationship_type VARCHAR(80) NOT NULL,
    is_owner BOOLEAN NOT NULL DEFAULT FALSE,
    linked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(employee_id, agent_goal_id, relationship_type)
);

-- 40. employee_agent_skill_inheritance [R]
CREATE TABLE employee_agent_skill_inheritance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    employee_id UUID NOT NULL REFERENCES employee(id),
    agent_id UUID NOT NULL REFERENCES agent(id),
    skill_id UUID NOT NULL REFERENCES master_skill(id),
    inheritance_mode VARCHAR(80) NOT NULL,
    confidence_cap NUMERIC(5,2) NULL,
    effective_from TIMESTAMPTZ NULL,
    effective_to TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(employee_id, agent_id, skill_id, inheritance_mode)
);

-- 41. agent_reporting_line [R]
CREATE TABLE agent_reporting_line (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    child_agent_id UUID NOT NULL REFERENCES agent(id),
    parent_agent_id UUID NOT NULL REFERENCES agent(id),
    relationship_type VARCHAR(80) NOT NULL,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    start_at TIMESTAMPTZ NULL,
    end_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(child_agent_id, parent_agent_id, relationship_type, start_at)
);


-- ============================================
-- TABLE FAMILY 7: PRODUCT / PROJECT / GROUP DOMAIN
-- ============================================

-- 42. product [O]
CREATE TABLE product (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    code VARCHAR(80) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT NULL,
    owner_employee_id UUID NULL REFERENCES employee(id),
    status VARCHAR(40) NOT NULL DEFAULT 'active', -- [R]
    launch_date DATE NULL,
    retirement_date DATE NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL,
    UNIQUE(tenant_id, code)
);

CREATE INDEX idx_product_tenant ON product(tenant_id);

-- 43. project [O]
CREATE TABLE project (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    product_id UUID NULL REFERENCES product(id),
    code VARCHAR(80) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT NULL,
    owner_employee_id UUID NULL REFERENCES employee(id),
    sponsor_identity_id UUID NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'proposed',
    start_date DATE NULL,
    target_end_date DATE NULL,
    actual_end_date DATE NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL,
    UNIQUE(tenant_id, code)
);

CREATE INDEX idx_project_tenant ON project(tenant_id);
CREATE INDEX idx_project_product ON project(product_id);

-- 44. group_entity [O]
CREATE TABLE group_entity (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    code VARCHAR(80) NOT NULL,
    name VARCHAR(200) NOT NULL,
    group_type VARCHAR(40) NOT NULL,
    parent_group_id UUID NULL REFERENCES group_entity(id),
    owner_identity_id UUID NULL,
    description TEXT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL,
    UNIQUE(tenant_id, code)
);

CREATE INDEX idx_group_entity_tenant ON group_entity(tenant_id);
CREATE INDEX idx_group_entity_type ON group_entity(group_type);

-- 45. product_project_group_link [R]
CREATE TABLE product_project_group_link (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    product_id UUID NULL REFERENCES product(id),
    project_id UUID NULL REFERENCES project(id),
    group_id UUID NULL REFERENCES group_entity(id),
    link_type VARCHAR(80) NOT NULL,
    linked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    linked_by_identity_id UUID NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_link_product ON product_project_group_link(product_id);
CREATE INDEX idx_link_project ON product_project_group_link(project_id);
CREATE INDEX idx_link_group ON product_project_group_link(group_id);


-- ============================================
-- TABLE FAMILY 8: WORKFLOW DOMAIN
-- ============================================

-- 46. task [O]
CREATE TABLE task (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    product_id UUID NULL REFERENCES product(id),
    project_id UUID NULL REFERENCES project(id),
    group_id UUID NULL REFERENCES group_entity(id),
    decision_id UUID NULL,
    title VARCHAR(240) NOT NULL,
    description TEXT NULL,
    task_type VARCHAR(80) NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'open',
    priority INTEGER NOT NULL DEFAULT 3,
    requester_identity_id UUID NULL,
    owner_identity_id UUID NULL,
    assigned_employee_id UUID NULL REFERENCES employee(id),
    assigned_agent_id UUID NULL REFERENCES agent(id),
    start_at TIMESTAMPTZ NULL,
    due_at TIMESTAMPTZ NULL,
    sla_due_at TIMESTAMPTZ NULL,
    completed_at TIMESTAMPTZ NULL,
    blocked_reason TEXT NULL,
    task_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL
);

CREATE INDEX idx_task_tenant ON task(tenant_id);
CREATE INDEX idx_task_status ON task(status);
CREATE INDEX idx_task_owner ON task(owner_identity_id);
CREATE INDEX idx_task_assigned_employee ON task(assigned_employee_id);
CREATE INDEX idx_task_assigned_agent ON task(assigned_agent_id);
CREATE INDEX idx_task_due_at ON task(due_at);

-- 47. milestone [R]
CREATE TABLE milestone (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    project_id UUID NULL REFERENCES project(id),
    product_id UUID NULL REFERENCES product(id),
    title VARCHAR(240) NOT NULL,
    description TEXT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'open', -- [R]
    target_date TIMESTAMPTZ NULL,
    completed_at TIMESTAMPTZ NULL,
    owner_identity_id UUID NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_milestone_project ON milestone(project_id);
CREATE INDEX idx_milestone_product ON milestone(product_id);

-- 48. reminder [O]
CREATE TABLE reminder (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    task_id UUID NULL REFERENCES task(id),
    milestone_id UUID NULL,
    decision_id UUID NULL,
    target_identity_id UUID NOT NULL,
    channel_id UUID NULL REFERENCES master_channel(id),
    reminder_type VARCHAR(80) NULL,
    scheduled_for TIMESTAMPTZ NOT NULL,
    sent_at TIMESTAMPTZ NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'scheduled',
    snoozed_until TIMESTAMPTZ NULL,
    message_template TEXT NULL,
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_reminder_target ON reminder(target_identity_id);
CREATE INDEX idx_reminder_scheduled_for ON reminder(scheduled_for);
CREATE INDEX idx_reminder_status ON reminder(status);

-- 49. escalation [O]
CREATE TABLE escalation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    task_id UUID NULL REFERENCES task(id),
    approval_id UUID NULL,
    decision_id UUID NULL,
    escalation_code VARCHAR(80) NULL,
    title VARCHAR(240) NOT NULL,
    reason TEXT NULL,
    triggered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    target_identity_id UUID NULL,
    target_group_id UUID NULL,
    severity VARCHAR(40) NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'open',
    resolved_at TIMESTAMPTZ NULL,
    resolution_notes TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_escalation_task ON escalation(task_id);
CREATE INDEX idx_escalation_status ON escalation(status);
CREATE INDEX idx_escalation_target ON escalation(target_identity_id);

-- 50. delegation [O]
CREATE TABLE delegation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    delegator_identity_id UUID NOT NULL,
    delegate_identity_id UUID NOT NULL,
    scope_type VARCHAR(80) NOT NULL,
    scope_id UUID NULL,
    start_at TIMESTAMPTZ NOT NULL,
    end_at TIMESTAMPTZ NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'active', -- [R]
    constraints_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_delegation_delegator ON delegation(delegator_identity_id);
CREATE INDEX idx_delegation_delegate ON delegation(delegate_identity_id);


-- ============================================
-- TABLE FAMILY 9: CHANNELS AND FILES
-- ============================================

-- 51. channel_account [R]
CREATE TABLE channel_account (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    channel_id UUID NOT NULL REFERENCES master_channel(id),
    identity_id UUID NULL,
    agent_id UUID NULL REFERENCES agent(id),
    external_account_ref VARCHAR(200) NULL,
    handle VARCHAR(160) NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'active', -- [R]
    config_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_channel_account_channel ON channel_account(channel_id);

-- 52. conversation_thread [R]
CREATE TABLE conversation_thread (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    channel_account_id UUID NULL REFERENCES channel_account(id),
    project_id UUID NULL REFERENCES project(id),
    decision_id UUID NULL,
    thread_key VARCHAR(200) NULL,
    title VARCHAR(240) NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'active', -- [R]
    opened_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at TIMESTAMPTZ NULL,
    context_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_thread_channel ON conversation_thread(channel_account_id);
CREATE INDEX idx_thread_project ON conversation_thread(project_id);

-- 53. message_event [R]
CREATE TABLE message_event (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    thread_id UUID NOT NULL REFERENCES conversation_thread(id),
    sender_identity_id UUID NULL,
    sender_agent_id UUID NULL REFERENCES agent(id),
    message_type VARCHAR(80) NULL,
    body_text TEXT NULL,
    body_json JSONB NULL,
    external_message_ref VARCHAR(200) NULL,
    sent_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    edited_at TIMESTAMPTZ NULL,
    message_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_message_thread ON message_event(thread_id);
CREATE INDEX idx_message_sent_at ON message_event(sent_at);

-- 54. file_asset [O]
CREATE TABLE file_asset (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    file_name VARCHAR(255) NOT NULL,
    file_ext VARCHAR(20) NULL,
    mime_type VARCHAR(120) NULL,
    file_size_bytes BIGINT NULL,
    storage_uri TEXT NOT NULL,
    checksum_sha256 VARCHAR(64) NULL,
    uploaded_by_identity_id UUID NULL,
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    classification VARCHAR(80) NULL,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_file_asset_tenant ON file_asset(tenant_id);

-- 55. file_link [O]
CREATE TABLE file_link (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    file_asset_id UUID NOT NULL REFERENCES file_asset(id),
    linked_entity_type VARCHAR(80) NOT NULL,
    linked_entity_id UUID NOT NULL,
    link_role VARCHAR(80) NULL,
    linked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    linked_by_identity_id UUID NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_file_link_asset ON file_link(file_asset_id);
CREATE INDEX idx_file_link_entity ON file_link(linked_entity_type, linked_entity_id);


-- ============================================
-- TABLE FAMILY 10: DECISION WORKSPACE / DECISION CONTROL PLANE
-- ============================================

-- 56. decision [O] - CORE decision table
CREATE TABLE decision (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    product_id UUID NULL REFERENCES product(id),
    project_id UUID NULL REFERENCES project(id),
    group_id UUID NULL REFERENCES group_entity(id),
    partner_account_id UUID NULL REFERENCES partner_account(id),
    title VARCHAR(240) NOT NULL,
    decision_category VARCHAR(120) NULL,
    problem_statement TEXT NOT NULL,
    scope_text TEXT NULL,
    sponsor_identity_id UUID NULL,
    owner_identity_id UUID NULL,
    requested_by_identity_id UUID NULL,
    risk_level VARCHAR(40) NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'intake',
    recommendation_summary TEXT NULL,
    recommended_option_id UUID NULL,
    target_review_date DATE NULL,
    decided_at TIMESTAMPTZ NULL,
    archived_at TIMESTAMPTZ NULL,
    decision_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL
);

CREATE INDEX idx_decision_tenant ON decision(tenant_id);
CREATE INDEX idx_decision_status ON decision(status);
CREATE INDEX idx_decision_sponsor ON decision(sponsor_identity_id);
CREATE INDEX idx_decision_owner ON decision(owner_identity_id);
CREATE INDEX idx_decision_target_review ON decision(target_review_date);

-- 57. decision_workspace [O] - Decision context workspace
CREATE TABLE decision_workspace (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    decision_id UUID UNIQUE NOT NULL REFERENCES decision(id),
    workspace_slug VARCHAR(160) NULL,
    current_brief TEXT NULL,
    current_context_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    current_constraints_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    current_assumptions_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    current_stakeholders_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    current_outcome_hypothesis TEXT NULL,
    last_compacted_at TIMESTAMPTZ NULL,
    workspace_version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 58. decision_alternative [O]
CREATE TABLE decision_alternative (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    decision_id UUID NOT NULL REFERENCES decision(id),
    option_code VARCHAR(80) NULL,
    title VARCHAR(240) NOT NULL,
    description TEXT NULL,
    estimated_cost NUMERIC(14,2) NULL,
    estimated_benefit NUMERIC(14,2) NULL,
    risk_summary TEXT NULL,
    feasibility_score NUMERIC(6,2) NULL,
    overall_score NUMERIC(6,2) NULL,
    is_recommended BOOLEAN NOT NULL DEFAULT FALSE,
    rank_order INTEGER NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_alt_decision ON decision_alternative(decision_id);

-- 59. decision_evidence [O]
CREATE TABLE decision_evidence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    decision_id UUID NOT NULL REFERENCES decision(id),
    evidence_type VARCHAR(40) NOT NULL,
    title VARCHAR(240) NOT NULL,
    source_system VARCHAR(120) NULL,
    source_ref VARCHAR(240) NULL,
    file_asset_id UUID NULL REFERENCES file_asset(id),
    thread_id UUID NULL,
    metric_name VARCHAR(160) NULL,
    metric_value_text VARCHAR(160) NULL,
    excerpt_text TEXT NULL,
    evidence_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    captured_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_evidence_decision ON decision_evidence(decision_id);
CREATE INDEX idx_evidence_type ON decision_evidence(evidence_type);

-- 60. decision_assumption [O]
CREATE TABLE decision_assumption (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    decision_id UUID NOT NULL REFERENCES decision(id),
    assumption_text TEXT NOT NULL,
    confidence_score NUMERIC(5,2) NULL,
    source_evidence_id UUID NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'active', -- [R]
    validated_at TIMESTAMPTZ NULL,
    invalidated_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_assumption_decision ON decision_assumption(decision_id);

-- 61. decision_constraint [O]
CREATE TABLE decision_constraint (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    decision_id UUID NOT NULL REFERENCES decision(id),
    constraint_type VARCHAR(80) NOT NULL,
    constraint_text TEXT NOT NULL,
    hard_limit BOOLEAN NOT NULL DEFAULT TRUE,
    source_policy_id UUID NULL,
    source_entity_type VARCHAR(80) NULL,
    source_entity_id UUID NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_constraint_decision ON decision_constraint(decision_id);

-- 62. decision_scorecard [O]
CREATE TABLE decision_scorecard (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    decision_id UUID NOT NULL REFERENCES decision(id),
    alternative_id UUID NOT NULL REFERENCES decision_alternative(id),
    criterion_name VARCHAR(160) NOT NULL,
    criterion_weight NUMERIC(6,3) NULL,
    raw_score NUMERIC(8,3) NULL,
    normalized_score NUMERIC(8,3) NULL,
    rationale TEXT NULL,
    scored_by_identity_id UUID NULL,
    scored_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_scorecard_decision ON decision_scorecard(decision_id);
CREATE INDEX idx_scorecard_alternative ON decision_scorecard(alternative_id);

-- 63. decision_outcome_review [O]
CREATE TABLE decision_outcome_review (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    decision_id UUID NOT NULL REFERENCES decision(id),
    review_date DATE NOT NULL,
    outcome_summary TEXT NULL,
    success_rating NUMERIC(5,2) NULL,
    assumptions_held_count INTEGER NULL,
    assumptions_failed_count INTEGER NULL,
    lessons_learned TEXT NULL,
    followup_decision_needed BOOLEAN NOT NULL DEFAULT FALSE,
    reviewed_by_identity_id UUID NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_outcome_review_decision ON decision_outcome_review(decision_id);


-- ============================================
-- TABLE FAMILY 11: APPROVAL / OVERRIDE / GOVERNANCE
-- ============================================

-- 64. approval [O]
CREATE TABLE approval (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    subject_type VARCHAR(80) NOT NULL,
    subject_id UUID NOT NULL,
    request_title VARCHAR(240) NOT NULL,
    request_reason TEXT NULL,
    requested_by_identity_id UUID NOT NULL,
    current_status VARCHAR(40) NOT NULL DEFAULT 'pending',
    required_by_at TIMESTAMPTZ NULL,
    decided_at TIMESTAMPTZ NULL,
    final_decider_identity_id UUID NULL,
    decision_notes TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_approval_tenant ON approval(tenant_id);
CREATE INDEX idx_approval_status ON approval(current_status);
CREATE INDEX idx_approval_required_by ON approval(required_by_at);
CREATE INDEX idx_approval_subject ON approval(subject_type, subject_id);

-- 65. approval_step [R]
CREATE TABLE approval_step (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    approval_id UUID NOT NULL REFERENCES approval(id),
    step_order INTEGER NOT NULL,
    approver_identity_id UUID NULL,
    approver_group_id UUID NULL,
    rule_type VARCHAR(80) NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'pending',
    required BOOLEAN NOT NULL DEFAULT TRUE,
    acted_at TIMESTAMPTZ NULL,
    action_notes TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(approval_id, step_order)
);

CREATE INDEX idx_approval_step_approval ON approval_step(approval_id);

-- 66. override_event [O]
CREATE TABLE override_event (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    subject_type VARCHAR(80) NOT NULL,
    subject_id UUID NOT NULL,
    override_type VARCHAR(80) NOT NULL,
    reason TEXT NOT NULL,
    requested_by_identity_id UUID NOT NULL,
    approved_by_identity_id UUID NULL,
    effective_from TIMESTAMPTZ NOT NULL DEFAULT now(),
    effective_to TIMESTAMPTZ NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'active', -- [R]
    override_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_override_subject ON override_event(subject_type, subject_id);

-- 67. policy_bundle [O]
CREATE TABLE policy_bundle (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    bundle_code VARCHAR(80) NOT NULL,
    name VARCHAR(200) NOT NULL,
    version_label VARCHAR(80) NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'draft', -- [R]
    source_repo_ref TEXT NULL,
    bundle_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    activated_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(tenant_id, bundle_code, version_label)
);

CREATE INDEX idx_policy_bundle_tenant ON policy_bundle(tenant_id);

-- 68. policy_rule [O]
CREATE TABLE policy_rule (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    policy_bundle_id UUID NOT NULL REFERENCES policy_bundle(id),
    policy_type_id UUID NULL,
    rule_code VARCHAR(80) NOT NULL,
    name VARCHAR(200) NOT NULL,
    effect VARCHAR(40) NOT NULL,
    priority INTEGER NOT NULL DEFAULT 100,
    target_type VARCHAR(80) NULL,
    condition_expr TEXT NULL,
    rule_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(policy_bundle_id, rule_code)
);

CREATE INDEX idx_policy_rule_bundle ON policy_rule(policy_bundle_id);

-- 69. rbac_role [O]
CREATE TABLE rbac_role (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    role_code VARCHAR(80) NOT NULL,
    name VARCHAR(160) NOT NULL,
    description TEXT NULL,
    is_system BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(tenant_id, role_code)
);

CREATE INDEX idx_rbac_role_tenant ON rbac_role(tenant_id);

-- 70. rbac_role_binding [O]
CREATE TABLE rbac_role_binding (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    role_id UUID NOT NULL REFERENCES rbac_role(id),
    principal_type VARCHAR(40) NOT NULL,
    principal_id UUID NOT NULL,
    scope_type VARCHAR(80) NULL,
    scope_id UUID NULL,
    start_at TIMESTAMPTZ NULL,
    end_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(role_id, principal_type, principal_id, scope_type, scope_id)
);

CREATE INDEX idx_role_binding_role ON rbac_role_binding(role_id);
CREATE INDEX idx_role_binding_principal ON rbac_role_binding(principal_type, principal_id);

-- 71. tool_permission [O]
CREATE TABLE tool_permission (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    principal_type VARCHAR(40) NOT NULL,
    principal_id UUID NOT NULL,
    tool_code VARCHAR(120) NOT NULL,
    permission_level VARCHAR(80) NOT NULL,
    scope_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    effective_from TIMESTAMPTZ NULL,
    effective_to TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(principal_type, principal_id, tool_code, permission_level)
);

CREATE INDEX idx_tool_permission_principal ON tool_permission(principal_type, principal_id);


-- ============================================
-- TABLE FAMILY 12: EXECUTION / RUNTIME / MEMORY / AUDIT
-- ============================================

-- 72. execution_request [O]
CREATE TABLE execution_request (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    task_id UUID NULL,
    decision_id UUID NULL REFERENCES decision(id),
    requested_by_identity_id UUID NULL,
    requested_for_agent_id UUID NULL REFERENCES agent(id),
    request_type VARCHAR(80) NOT NULL,
    preferred_runtime_type VARCHAR(80) NULL,
    selected_runtime_type VARCHAR(80) NULL,
    fallback_runtime_type VARCHAR(80) NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'queued', -- [R]
    request_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    queued_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at TIMESTAMPTZ NULL,
    finished_at TIMESTAMPTZ NULL,
    error_text TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_exec_request_tenant ON execution_request(tenant_id);
CREATE INDEX idx_exec_request_status ON execution_request(status);
CREATE INDEX idx_exec_request_runtime ON execution_request(selected_runtime_type);
CREATE INDEX idx_exec_request_queued_at ON execution_request(queued_at);

-- 73. execution_record [O]
CREATE TABLE execution_record (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    execution_request_id UUID NOT NULL REFERENCES execution_request(id),
    agent_id UUID NULL REFERENCES agent(id),
    runtime_type VARCHAR(80) NOT NULL,
    provider_name VARCHAR(120) NULL,
    model_name VARCHAR(160) NULL,
    trace_id VARCHAR(160) NULL,
    span_id VARCHAR(160) NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'running', -- [R]
    input_tokens INTEGER NULL,
    output_tokens INTEGER NULL,
    estimated_cost NUMERIC(12,4) NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ NULL,
    execution_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_exec_record_request ON execution_record(execution_request_id);
CREATE INDEX idx_exec_record_agent ON execution_record(agent_id);

-- 74. memory_record [O] - 9-layer memory model entries
CREATE TABLE memory_record (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    layer_type VARCHAR(40) NOT NULL, -- working|episodic|semantic|operational|cortex|vector|checkpoint|audit|decision_workspace
    identity_id UUID NULL REFERENCES identity(id),
    agent_id UUID NULL REFERENCES agent(id),
    thread_id UUID NULL,
    decision_id UUID NULL REFERENCES decision(id),
    task_id UUID NULL,
    record_key VARCHAR(200) NULL,
    content_text TEXT NULL,
    content_json JSONB NULL,
    vector_ref VARCHAR(200) NULL,
    retention_until TIMESTAMPTZ NULL,
    relevance_score NUMERIC(6,3) NULL,
    source_execution_record_id UUID NULL,
    captured_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_memory_tenant ON memory_record(tenant_id);
CREATE INDEX idx_memory_layer ON memory_record(layer_type);
CREATE INDEX idx_memory_agent ON memory_record(agent_id);
CREATE INDEX idx_memory_decision ON memory_record(decision_id);
CREATE INDEX idx_memory_captured_at ON memory_record(captured_at);

-- 75. memory_checkpoint [O] - Checkpoints for agent state
CREATE TABLE memory_checkpoint (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    agent_id UUID NULL REFERENCES agent(id),
    thread_id UUID NULL,
    decision_id UUID NULL REFERENCES decision(id),
    checkpoint_label VARCHAR(160) NULL,
    checkpoint_version INTEGER NOT NULL DEFAULT 1,
    summary_text TEXT NULL,
    state_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    compacted_from_record_count INTEGER NULL,
    created_from_execution_record_id UUID NULL,
    checkpointed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_checkpoint_agent ON memory_checkpoint(agent_id);
CREATE INDEX idx_checkpoint_thread ON memory_checkpoint(thread_id);
CREATE INDEX idx_checkpoint_decision ON memory_checkpoint(decision_id);

-- 76. audit_event [O]
CREATE TABLE audit_event (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    event_time TIMESTAMPTZ NOT NULL DEFAULT now(),
    actor_identity_id UUID NULL,
    actor_agent_id UUID NULL,
    event_type VARCHAR(120) NOT NULL,
    subject_type VARCHAR(80) NOT NULL,
    subject_id UUID NOT NULL,
    action VARCHAR(120) NOT NULL,
    outcome VARCHAR(80) NULL,
    severity VARCHAR(40) NULL,
    correlation_id VARCHAR(160) NULL,
    request_id VARCHAR(160) NULL,
    ip_address INET NULL, -- [R]
    user_agent TEXT NULL, -- [R]
    before_json JSONB NULL,
    after_json JSONB NULL,
    event_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_tenant ON audit_event(tenant_id);
CREATE INDEX idx_audit_event_time ON audit_event(event_time);
CREATE INDEX idx_audit_event_type ON audit_event(event_type);
CREATE INDEX idx_audit_subject ON audit_event(subject_type, subject_id);
CREATE INDEX idx_audit_actor ON audit_event(actor_identity_id);


-- ============================================
-- ADDITIONAL OPERATIONAL CONSTRAINTS
-- ============================================

-- FK constraint for employee_group_membership.group_id (references group_entity)
ALTER TABLE employee_group_membership 
    ADD CONSTRAINT fk_emp_group_membership_group 
    FOREIGN KEY (group_id) REFERENCES group_entity(id) ON DELETE CASCADE;

-- FK constraint for agent_group_membership.group_id
ALTER TABLE agent_group_membership 
    ADD CONSTRAINT fk_agent_group_membership_group 
    FOREIGN KEY (group_id) REFERENCES group_entity(id) ON DELETE CASCADE;

-- FK constraint for task.group_id
ALTER TABLE task 
    ADD CONSTRAINT fk_task_group 
    FOREIGN KEY (group_id) REFERENCES group_entity(id) ON DELETE SET NULL;

-- FK constraint for task.decision_id
ALTER TABLE task 
    ADD CONSTRAINT fk_task_decision 
    FOREIGN KEY (decision_id) REFERENCES decision(id) ON DELETE SET NULL;

-- FK constraint for delegation.scope_id (can point to various entities, using check)
-- Note: Delegation scope is polymorphic; validation should be in application layer

-- ============================================
-- ENUMERATION VALUE CHECK CONSTRAINTS
-- ============================================

-- identity_type check
ALTER TABLE identity 
    ADD CONSTRAINT chk_identity_type 
    CHECK (identity_type IN ('human', 'agent', 'service', 'partner_user', 'external_system'));

-- organization_type check
ALTER TABLE tenant 
    ADD CONSTRAINT chk_organization_type 
    CHECK (organization_type IN ('tenant', 'partner', 'vendor', 'internal_department', 'customer'));

-- employee_status check
ALTER TABLE employee 
    ADD CONSTRAINT chk_employment_status 
    CHECK (employment_status IN ('invited', 'active', 'suspended', 'inactive', 'terminated'));

-- agent_status check  
ALTER TABLE agent 
    ADD CONSTRAINT chk_agent_status 
    CHECK (status IN ('requested', 'approved', 'active', 'suspended', 'expired', 'revoked', 'archived'));

-- task_status check
ALTER TABLE task 
    ADD CONSTRAINT chk_task_status 
    CHECK (status IN ('draft', 'open', 'in_progress', 'blocked', 'waiting_approval', 'completed', 'cancelled', 'failed'));

-- decision_status check
ALTER TABLE decision 
    ADD CONSTRAINT chk_decision_status 
    CHECK (status IN ('intake', 'in_analysis', 'recommendation_ready', 'pending_approval', 'approved', 'rejected', 'executed', 'reviewed', 'archived'));

-- approval_status check
ALTER TABLE approval 
    ADD CONSTRAINT chk_approval_status 
    CHECK (current_status IN ('pending', 'approved', 'rejected', 'withdrawn', 'expired'));

-- membership status checks
ALTER TABLE organization_membership 
    ADD CONSTRAINT chk_org_membership_status 
    CHECK (status IN ('active', 'inactive'));

ALTER TABLE employee_group_membership 
    ADD CONSTRAINT chk_emp_group_membership_status 
    CHECK (status IN ('active', 'inactive'));

ALTER TABLE agent_group_membership 
    ADD CONSTRAINT chk_agent_group_membership_status 
    CHECK (status IN ('active', 'inactive'));


-- ============================================
-- COMPLETION METADATA
-- ============================================
-- Schema version: v2-complete
-- Total tables: 76
-- Table families: 12
-- Generated: 2026-04-20
-- 
-- Validation notes:
-- - [O] = Original from recovered artifacts
-- - [R] = Reconstructed from architecture inference
-- ============================================