-- Migration 006: Channels and Files
-- Purpose: Create communication and file-sharing infrastructure.
-- Channels are conversation surfaces attached to products, projects, groups, or direct messages.
-- File assets are stored files that can be shared in channels.
--
-- Tables:
-- - channel
-- - channel_membership
-- - channel_message
-- - file_asset
-- - channel_file
--
-- ERD Mapping:
-- - channel belongs to tenant, references context (product/project/group)
-- - channel_membership links channel to employees/agents/groups
-- - channel_message belongs to channel
-- - file_asset belongs to tenant
-- - channel_file links file to channel (optionally to message)
--
-- Dependencies: 002_tenant_and_employee (tenant, employee), 003_agent_layer (agent), 004_product_project_group (product, group_entity)

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

-- Index for channel context lookups
CREATE INDEX idx_channel_context ON channel(context_type, context_id);