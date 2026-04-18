-- Migration 008: Tenant Policy and Control
-- Purpose: Create tenant-level policy and control tables.
-- These tables enforce tenant-specific routing, budget, and capability rules.
--
-- Tables (3):
-- - tenant_policy
-- - tenant_policy_backend_rule
-- - tenant_capability_policy
--
-- ERD Mapping: Section 7 (Decision and Control Plane - tenant policy)
-- Dependencies: 002 (tenant), 007 (decision/control plane base)

-- ============================================
-- TENANT POLICY
-- ============================================

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

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX idx_tenant_policy_tenant ON tenant_policy(tenant_id);