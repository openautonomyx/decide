-- Migration 003: Agent Layer
-- Purpose: Create AI agent entities and their relationships to employees.
-- Agents are associated with tenants and may have relationships with employees.
--
-- Tables:
-- - agent
-- - agent_identity
-- - agent_profile
-- - agent_goal
-- - agent_skill
-- - agent_governance_profile
-- - agent_memory_profile
-- - employee_agent_assignment
-- - agent_relationship
--
-- ERD Mapping:
-- - agent belongs to tenant
-- - agent_identity/profile/goal/skill/governance/memory belong to agent
-- - employee_agent_assignment links employee to agent
-- - agent_relationship defines agent-to-agent or agent-to-employee relationships
--
-- Dependencies: 002_tenant_and_employee (tenant, employee)

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

-- Index for agent lookup by tenant
CREATE INDEX idx_agent_tenant ON agent(tenant_id);