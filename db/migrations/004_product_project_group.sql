-- Migration 004: Product, Project, Group
-- Purpose: Create collaboration containers - organizational units for work and community.
-- Product (long-lived business entity), Project (short-term execution), Group (community).
--
-- Tables (4):
-- - product
-- - project
-- - group_entity
-- - group_membership
--
-- ERD Mapping: Section 3 (Collaboration Containers)
-- Dependencies: 002 (tenant), 003 (agent)

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