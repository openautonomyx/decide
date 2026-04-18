-- Autonomyx Data Model Schema v1
-- Complete normalized schema for the Autonomyx decision-intelligence platform.
-- 
-- Design principles:
-- - Human (employee) and agent are separate entities
-- - Employee may have multiple agents, with one primary human-facing agent representable
-- - Agents may report to agents or employees
-- - Product (persistent), project (short-term), group (community) are distinct
-- - Prompt, skills, goals, timelines are first-class design layers
-- - Approval and rule-based decisions are separate entity types
-- - Overrides and responsibility assignments are first-class

-- ============================================
-- CORE ORGANIZATION
-- ============================================

CREATE TABLE tenant (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE employee (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenant(id),
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE employee_identity (
    id VARCHAR(36) PRIMARY KEY,
    employee_id VARCHAR(36) NOT NULL REFERENCES employee(id),
    job_title VARCHAR(255),
    department VARCHAR(255),
    seniority VARCHAR(50),
    reporting_to_employee_id VARCHAR(36) REFERENCES employee(id),
    effective_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effective_to TIMESTAMP
);

CREATE TABLE employee_employment (
    id VARCHAR(36) PRIMARY KEY,
    employee_id VARCHAR(36) NOT NULL REFERENCES employee(id),
    start_date DATE NOT NULL,
    end_date DATE,
    employment_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE employee_education (
    id VARCHAR(36) PRIMARY KEY,
    employee_id VARCHAR(36) NOT NULL REFERENCES employee(id),
    institution VARCHAR(255),
    degree VARCHAR(255),
    field_of_study VARCHAR(255),
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE employee_certification (
    id VARCHAR(36) PRIMARY KEY,
    employee_id VARCHAR(36) NOT NULL REFERENCES employee(id),
    certification_code VARCHAR(50),
    certification_name VARCHAR(255),
    issued_date DATE,
    expiry_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- AGENT LAYER
-- ============================================

CREATE TABLE agent (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenant(id),
    name VARCHAR(255) NOT NULL,
    agent_type VARCHAR(50),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agent_identity (
    id VARCHAR(36) PRIMARY KEY,
    agent_id VARCHAR(36) NOT NULL REFERENCES agent(id),
    projected_title VARCHAR(255),
    projected_department VARCHAR(255),
    effective_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effective_to TIMESTAMP
);

CREATE TABLE agent_profile (
    id VARCHAR(36) PRIMARY KEY,
    agent_id VARCHAR(36) NOT NULL REFERENCES agent(id),
    behavioral_profile JSONB,
    operational_profile JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agent_goal (
    id VARCHAR(36) PRIMARY KEY,
    agent_id VARCHAR(36) NOT NULL REFERENCES agent(id),
    goal_type VARCHAR(50),
    description TEXT,
    target_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agent_skill (
    id VARCHAR(36) PRIMARY KEY,
    agent_id VARCHAR(36) NOT NULL REFERENCES agent(id),
    skill_code VARCHAR(50) NOT NULL,
    skill_name VARCHAR(255),
    proficiency_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agent_governance_profile (
    id VARCHAR(36) PRIMARY KEY,
    agent_id VARCHAR(36) NOT NULL REFERENCES agent(id),
    prompt_profile_id VARCHAR(36),
    guardrail_profile_id VARCHAR(36),
    approval_profile_id VARCHAR(36),
    channel_profile_id VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agent_memory_profile (
    id VARCHAR(36) PRIMARY KEY,
    agent_id VARCHAR(36) NOT NULL REFERENCES agent(id),
    memory_enabled BOOLEAN DEFAULT TRUE,
    thread_retention_days INTEGER DEFAULT 30,
    checkpoint_interval_seconds INTEGER DEFAULT 60,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE employee_agent_assignment (
    id VARCHAR(36) PRIMARY KEY,
    employee_id VARCHAR(36) NOT NULL REFERENCES employee(id),
    agent_id VARCHAR(36) NOT NULL REFERENCES agent(id),
    assignment_role VARCHAR(50) NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP
);

CREATE TABLE agent_relationship (
    id VARCHAR(36) PRIMARY KEY,
    from_agent_id VARCHAR(36) REFERENCES agent(id),
    to_agent_id VARCHAR(36) REFERENCES agent(id),
    to_employee_id VARCHAR(36) REFERENCES employee(id),
    relationship_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- COLLABORATION CONTAINERS
-- ============================================

CREATE TABLE product (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenant(id),
    name VARCHAR(255) NOT NULL,
    strategy TEXT,
    primary_channel_id VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE project (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenant(id),
    name VARCHAR(255) NOT NULL,
    start_date DATE,
    end_date DATE,
    channel_id VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE group_entity (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenant(id),
    name VARCHAR(255) NOT NULL,
    group_type VARCHAR(50),
    primary_channel_id VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE group_membership (
    id VARCHAR(36) PRIMARY KEY,
    group_id VARCHAR(36) NOT NULL REFERENCES group_entity(id),
    member_type VARCHAR(20) NOT NULL,
    member_id VARCHAR(36) NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP
);

-- ============================================
-- WORKFLOW ENTITIES
-- ============================================

CREATE TABLE task (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenant(id),
    project_id VARCHAR(36) REFERENCES project(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    priority VARCHAR(20),
    assigned_to_employee_id VARCHAR(36) REFERENCES employee(id),
    assigned_to_agent_id VARCHAR(36) REFERENCES agent(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE task_dependency (
    id VARCHAR(36) PRIMARY KEY,
    task_id VARCHAR(36) NOT NULL REFERENCES task(id),
    depends_on_task_id VARCHAR(36) NOT NULL REFERENCES task(id),
    dependency_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE task_assignment_history (
    id VARCHAR(36) PRIMARY KEY,
    task_id VARCHAR(36) NOT NULL REFERENCES task(id),
    assigned_from_type VARCHAR(20),
    assigned_from_id VARCHAR(36),
    assigned_to_type VARCHAR(20),
    assigned_to_id VARCHAR(36),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by VARCHAR(36) REFERENCES employee(id)
);

CREATE TABLE deadline (
    id VARCHAR(36) PRIMARY KEY,
    task_id VARCHAR(36) NOT NULL REFERENCES task(id),
    due_at TIMESTAMP NOT NULL,
    reminder_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE milestone (
    id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) NOT NULL REFERENCES project(id),
    name VARCHAR(255) NOT NULL,
    target_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE milestone_task (
    id VARCHAR(36) PRIMARY KEY,
    milestone_id VARCHAR(36) NOT NULL REFERENCES milestone(id),
    task_id VARCHAR(36) NOT NULL REFERENCES task(id)
);

CREATE TABLE reminder (
    id VARCHAR(36) PRIMARY KEY,
    reminder_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(36) NOT NULL,
    remind_at TIMESTAMP NOT NULL,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE escalation (
    id VARCHAR(36) PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(36) NOT NULL,
    escalation_type VARCHAR(50) NOT NULL,
    reason TEXT,
    escalated_to_employee_id VARCHAR(36) REFERENCES employee(id),
    status VARCHAR(50) DEFAULT 'open',
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- WORKFLOW COLLABORATION
-- ============================================

CREATE TABLE task_comment (
    id VARCHAR(36) PRIMARY KEY,
    task_id VARCHAR(36) NOT NULL REFERENCES task(id),
    author_type VARCHAR(20) NOT NULL,
    author_id VARCHAR(36) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE task_comment_attachment (
    id VARCHAR(36) PRIMARY KEY,
    comment_id VARCHAR(36) NOT NULL REFERENCES task_comment(id),
    file_asset_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE task_attachment (
    id VARCHAR(36) PRIMARY KEY,
    task_id VARCHAR(36) NOT NULL REFERENCES task(id),
    file_asset_id VARCHAR(36) NOT NULL,
    attached_by_type VARCHAR(20),
    attached_by_id VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE task_rating (
    id VARCHAR(36) PRIMARY KEY,
    task_id VARCHAR(36) NOT NULL REFERENCES task(id),
    rating_type VARCHAR(50) NOT NULL,
    score INTEGER NOT NULL,
    rated_by_employee_id VARCHAR(36) REFERENCES employee(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE task_feedback (
    id VARCHAR(36) PRIMARY KEY,
    task_id VARCHAR(36) NOT NULL REFERENCES task(id),
    content TEXT NOT NULL,
    provided_by_employee_id VARCHAR(36) REFERENCES employee(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- CHANNELS AND FILE SHARING
-- ============================================

CREATE TABLE channel (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenant(id),
    context_type VARCHAR(50) NOT NULL,
    context_id VARCHAR(36),
    name VARCHAR(255) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE channel_membership (
    id VARCHAR(36) PRIMARY KEY,
    channel_id VARCHAR(36) NOT NULL REFERENCES channel(id),
    member_type VARCHAR(20) NOT NULL,
    member_id VARCHAR(36) NOT NULL,
    role VARCHAR(50) DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP
);

CREATE TABLE channel_message (
    id VARCHAR(36) PRIMARY KEY,
    channel_id VARCHAR(36) NOT NULL REFERENCES channel(id),
    author_type VARCHAR(20) NOT NULL,
    author_id VARCHAR(36) NOT NULL,
    content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'chat',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE file_asset (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenant(id),
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(100),
    file_size_bytes BIGINT,
    storage_path TEXT NOT NULL,
    uploaded_by_type VARCHAR(20),
    uploaded_by_id VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE channel_file (
    id VARCHAR(36) PRIMARY KEY,
    channel_id VARCHAR(36) NOT NULL REFERENCES channel(id),
    file_asset_id VARCHAR(36) NOT NULL REFERENCES file_asset(id),
    message_id VARCHAR(36) REFERENCES channel_message(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- DECISION AND CONTROL PLANE
-- ============================================

CREATE TABLE execution_request (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) REFERENCES tenant(id),
    goal TEXT NOT NULL,
    capability VARCHAR(50) NOT NULL,
    quality VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE execution_request_metadata (
    id VARCHAR(36) PRIMARY KEY,
    execution_request_id VARCHAR(36) NOT NULL REFERENCES execution_request(id),
    key VARCHAR(100) NOT NULL,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE policy_resolution (
    id VARCHAR(36) PRIMARY KEY,
    execution_request_id VARCHAR(36) NOT NULL REFERENCES execution_request(id),
    effective_policy JSONB NOT NULL,
    resolved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE backend_selection (
    id VARCHAR(36) PRIMARY KEY,
    execution_request_id VARCHAR(36) NOT NULL REFERENCES execution_request(id),
    selected_backend VARCHAR(50) NOT NULL,
    routing_reason TEXT,
    fallback_order JSONB,
    selected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE fallback_event (
    id VARCHAR(36) PRIMARY KEY,
    execution_request_id VARCHAR(36) NOT NULL REFERENCES execution_request(id),
    from_backend VARCHAR(50) NOT NULL,
    to_backend VARCHAR(50) NOT NULL,
    reason TEXT,
    occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE approval_request (
    id VARCHAR(36) PRIMARY KEY,
    execution_request_id VARCHAR(36) NOT NULL REFERENCES execution_request(id),
    status VARCHAR(50) DEFAULT 'pending',
    requested_by_type VARCHAR(20),
    requested_by_id VARCHAR(36),
    approver VARCHAR(36) REFERENCES employee(id),
    approver_notes TEXT,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    decided_at TIMESTAMP
);

CREATE TABLE decision_record (
    id VARCHAR(36) PRIMARY KEY,
    execution_request_id VARCHAR(36) NOT NULL REFERENCES execution_request(id),
    decision_type VARCHAR(50) NOT NULL,
    reason TEXT,
    decided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE override_record (
    id VARCHAR(36) PRIMARY KEY,
    execution_request_id VARCHAR(36) NOT NULL REFERENCES execution_request(id),
    override_type VARCHAR(50) NOT NULL,
    applied_by_type VARCHAR(20),
    applied_by_id VARCHAR(36),
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE responsibility_assignment (
    id VARCHAR(36) PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(36) NOT NULL,
    assignment_type VARCHAR(50) NOT NULL,
    from_type VARCHAR(20),
    from_id VARCHAR(36),
    to_type VARCHAR(20),
    to_id VARCHAR(36),
    effective_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effective_to TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE usage_record (
    id VARCHAR(36) PRIMARY KEY,
    execution_request_id VARCHAR(36) NOT NULL REFERENCES execution_request(id),
    backend_used VARCHAR(50) NOT NULL,
    provider VARCHAR(50),
    model VARCHAR(100),
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_tokens INTEGER,
    cost NUMERIC(10, 6),
    latency_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE memory_checkpoint (
    id VARCHAR(36) PRIMARY KEY,
    execution_request_id VARCHAR(36) NOT NULL REFERENCES execution_request(id),
    thread_id VARCHAR(36) NOT NULL,
    checkpoint_type VARCHAR(50) NOT NULL,
    checkpoint_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE execution_history (
    id VARCHAR(36) PRIMARY KEY,
    execution_request_id VARCHAR(36) NOT NULL REFERENCES execution_request(id),
    thread_id VARCHAR(36) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- MASTER DATA
-- ============================================

CREATE TABLE department_master (
    code VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    parent_department_code VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE job_title_master (
    code VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE seniority_level_master (
    code VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    level_order INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sfia_skill_master (
    code VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE certification_master (
    code VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    provider VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE institution_master (
    code VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    institution_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE qualification_type_master (
    code VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE topic_master (
    code VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PROFILE MASTERS (from prompt/skills/goal/timeline layer)
CREATE TABLE prompt_profile_master (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE prompt_template (
    id VARCHAR(36) PRIMARY KEY,
    profile_id VARCHAR(36) REFERENCES prompt_profile_master(id),
    name VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE prompt_template_version (
    id VARCHAR(36) PRIMARY KEY,
    template_id VARCHAR(36) NOT NULL REFERENCES prompt_template(id),
    version INTEGER NOT NULL,
    content TEXT NOT NULL,
    change_note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(36) REFERENCES employee(id)
);

CREATE TABLE agent_prompt_assignment (
    id VARCHAR(36) PRIMARY KEY,
    agent_id VARCHAR(36) NOT NULL REFERENCES agent(id),
    prompt_template_id VARCHAR(36) NOT NULL REFERENCES prompt_template(id),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by VARCHAR(36) REFERENCES employee(id),
    ended_at TIMESTAMP
);

-- Skill profiles for agents
CREATE TABLE skill_profile (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE skill_profile_skill (
    id VARCHAR(36) PRIMARY KEY,
    profile_id VARCHAR(36) NOT NULL REFERENCES skill_profile(id),
    skill_code VARCHAR(50) NOT NULL REFERENCES sfia_skill_master(code),
    proficiency_level VARCHAR(20) NOT NULL,
    is_core BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Goal success criteria and constraints
CREATE TABLE goal_success_criteria (
    id VARCHAR(36) PRIMARY KEY,
    goal_id VARCHAR(36) NOT NULL REFERENCES agent_goal(id),
    criteria_type VARCHAR(50) NOT NULL,
    criteria_value TEXT NOT NULL,
    weight NUMERIC(5, 2) DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE goal_constraint (
    id VARCHAR(36) PRIMARY KEY,
    goal_id VARCHAR(36) NOT NULL REFERENCES agent_goal(id),
    constraint_type VARCHAR(50) NOT NULL,
    constraint_value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Timeline for agent goal tracking
CREATE TABLE timeline (
    id VARCHAR(36) PRIMARY KEY,
    agent_id VARCHAR(36) NOT NULL REFERENCES agent(id),
    name VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE timeline_milestone (
    id VARCHAR(36) PRIMARY KEY,
    timeline_id VARCHAR(36) NOT NULL REFERENCES timeline(id),
    name VARCHAR(255) NOT NULL,
    target_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE timeline_deadline (
    id VARCHAR(36) PRIMARY KEY,
    timeline_id VARCHAR(36) NOT NULL REFERENCES timeline(id),
    name VARCHAR(255) NOT NULL,
    due_at TIMESTAMP NOT NULL,
    reminder_at TIMESTAMP,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE timeline_dependency (
    id VARCHAR(36) PRIMARY KEY,
    timeline_id VARCHAR(36) NOT NULL REFERENCES timeline(id),
    depends_on_timeline_id VARCHAR(36) NOT NULL REFERENCES timeline(id),
    dependency_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TENANT POLICY/CONTROL
CREATE TABLE tenant_policy (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenant(id),
    name VARCHAR(255) NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    quality_default VARCHAR(50),
    allow_fallback BOOLEAN DEFAULT TRUE,
    max_retries INTEGER DEFAULT 3,
    approval_required_for JSONB,
    max_budget_monthly NUMERIC(12, 2),
    max_requests_per_hour INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tenant_policy_backend_rule (
    id VARCHAR(36) PRIMARY KEY,
    policy_id VARCHAR(36) NOT NULL REFERENCES tenant_policy(id),
    backend_id VARCHAR(50) NOT NULL,
    rule_action VARCHAR(20) NOT NULL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tenant_capability_policy (
    id VARCHAR(36) PRIMARY KEY,
    policy_id VARCHAR(36) NOT NULL REFERENCES tenant_policy(id),
    capability VARCHAR(50) NOT NULL,
    max_tokens_per_request INTEGER,
    max_images_per_month INTEGER,
    rate_limit_per_hour INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AGENT GROUP MEMBERSHIP (for agent-to-group relationships)
CREATE TABLE agent_group_membership (
    id VARCHAR(36) PRIMARY KEY,
    group_id VARCHAR(36) NOT NULL REFERENCES group_entity(id),
    agent_id VARCHAR(36) NOT NULL REFERENCES agent(id),
    role VARCHAR(50) DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP
);

-- INDEXES
CREATE INDEX idx_employee_tenant ON employee(tenant_id);
CREATE INDEX idx_agent_tenant ON agent(tenant_id);
CREATE INDEX idx_task_project ON task(project_id);
CREATE INDEX idx_task_status ON task(status);
CREATE INDEX idx_channel_context ON channel(context_type, context_id);
CREATE INDEX idx_execution_request_tenant ON execution_request(tenant_id);
CREATE INDEX idx_execution_request_status ON execution_request(status);
CREATE INDEX idx_approval_request_status ON approval_request(status);
CREATE INDEX idx_usage_record_backend ON usage_record(backend_used);
CREATE INDEX idx_goal_agent ON agent_goal(agent_id);
CREATE INDEX idx_timeline_agent ON timeline(agent_id);
CREATE INDEX idx_tenant_policy_tenant ON tenant_policy(tenant_id);