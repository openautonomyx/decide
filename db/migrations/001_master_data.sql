-- Migration 001: Master Data
-- Purpose: Create all master/reference tables with no foreign key dependencies.
-- These tables provide lookup values and profile templates used by other entities.
--
-- Tables (12):
-- - department_master
-- - job_title_master
-- - seniority_level_master
-- - sfia_skill_master
-- - certification_master
-- - institution_master
-- - qualification_type_master
-- - topic_master
-- - prompt_profile_master
-- - guardrail_profile_master
-- - approval_profile_master
-- - channel_profile_master
--
-- ERD Mapping: All master data tables are standalone reference data with no FK dependencies.
-- Dependencies: None (runs first)

-- ============================================
-- MASTER DATA - Reference Tables
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

-- PROFILE MASTERS
CREATE TABLE prompt_profile_master (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE guardrail_profile_master (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    rules JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE approval_profile_master (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    rules JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE channel_profile_master (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    settings JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);