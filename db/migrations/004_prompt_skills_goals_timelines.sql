-- Migration 004: Prompt / Skills / Goals / Timelines
-- Purpose: Create prompt templates, skill profiles, goals, and timeline tables for agent design layers.
-- These tables extend agent capabilities with first-class prompt/skill/goal/timeline layers.
--
-- Tables (14):
-- - prompt_template
-- - prompt_template_version
-- - agent_prompt_assignment
-- - skill_profile
-- - skill_profile_skill
-- - agent_goal
-- - goal_success_criteria
-- - goal_constraint
-- - timeline
-- - timeline_milestone
-- - timeline_deadline
-- - timeline_dependency
-- - agent_group_membership
-- - skill_profile (moved from schema)
--
-- ERD Mapping: Section 2 (Agent Layer - prompt/skills/goals), Section 2 (Timeline)
-- Dependencies: 001 (master data), 002 (tenant), 003 (agent table only)

-- ============================================
-- PROMPT TEMPLATES
-- ============================================

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

-- ============================================
-- SKILL PROFILES
-- ============================================

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

-- ============================================
-- GOALS
-- ============================================

CREATE TABLE agent_goal (
    id VARCHAR(36) PRIMARY KEY,
    agent_id VARCHAR(36) NOT NULL REFERENCES agent(id),
    goal_type VARCHAR(50),
    description TEXT,
    target_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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

-- ============================================
-- TIMELINES
-- ============================================

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

-- ============================================
-- AGENT GROUP MEMBERSHIP
-- ============================================

CREATE TABLE agent_group_membership (
    id VARCHAR(36) PRIMARY KEY,
    group_id VARCHAR(36) NOT NULL REFERENCES group_entity(id),
    agent_id VARCHAR(36) NOT NULL REFERENCES agent(id),
    role VARCHAR(50) DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX idx_goal_agent ON agent_goal(agent_id);
CREATE INDEX idx_timeline_agent ON timeline(agent_id);