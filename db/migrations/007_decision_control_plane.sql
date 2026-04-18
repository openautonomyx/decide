-- Migration 007: Decision and Control Plane
-- Purpose: Create the execution tracking and audit infrastructure.
-- Records execution requests, policy resolutions, routing decisions, approvals, and usage.
--
-- Tables:
-- - execution_request
-- - execution_request_metadata
-- - policy_resolution
-- - backend_selection
-- - fallback_event
-- - approval_request
-- - decision_record
-- - override_record
-- - responsibility_assignment
-- - usage_record
-- - memory_checkpoint
-- - execution_history
--
-- ERD Mapping:
-- - execution_request belongs to tenant
-- - execution_request_metadata links to execution_request
-- - policy_resolution/backend_selection/fallback_event/approval_request/decision_record/override_record/usage_record/memory_checkpoint/execution_history all reference execution_request
-- - approval_request references employee as approver
-- - decision_record captures rule-based and human decisions
--
-- Dependencies: 002_tenant_and_employee (tenant, employee), 003_agent_layer (agent)

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

-- Indexes for execution queries
CREATE INDEX idx_execution_request_tenant ON execution_request(tenant_id);
CREATE INDEX idx_execution_request_status ON execution_request(status);
CREATE INDEX idx_approval_request_status ON approval_request(status);
CREATE INDEX idx_usage_record_backend ON usage_record(backend_used);