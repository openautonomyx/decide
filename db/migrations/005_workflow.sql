-- Migration 005: Workflow
-- Purpose: Create workflow entities for task management - tasks, milestones, deadlines, reminders, escalations.
-- Also includes task collaboration (comments, attachments, ratings, feedback).
--
-- Tables:
-- - task
-- - task_dependency
-- - task_assignment_history
-- - deadline
-- - milestone
-- - milestone_task
-- - reminder
-- - escalation
-- - task_comment
-- - task_comment_attachment
-- - task_attachment
-- - task_rating
-- - task_feedback
--
-- ERD Mapping:
-- - task belongs to tenant, optionally to project
-- - task references employees and agents for assignment
-- - task_dependency tracks task-to-task dependencies
-- - task_assignment_history audits ownership changes
-- - deadline/reminder/escalation reference task
-- - milestone references project
-- - milestone_task joins milestone and task
-- - task_comment/attachment/rating/feedback reference task
--
-- Dependencies: 002_tenant_and_employee (tenant, employee), 003_agent_layer (agent), 004_product_project_group (project)

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

-- Indexes for workflow queries
CREATE INDEX idx_task_project ON task(project_id);
CREATE INDEX idx_task_status ON task(status);