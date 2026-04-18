-- Migration 002: Tenant and Employee
-- Purpose: Create core organizational entities - tenant (organization boundary) and employee (human users).
-- These tables have no external dependencies and are foundational for all other entities.
--
-- Tables:
-- - tenant
-- - employee
-- - employee_identity
-- - employee_employment
-- - employee_education
-- - employee_certification
--
-- ERD Mapping: 
-- - tenant is the root entity for all organizational data
-- - employee belongs to tenant
-- - employee_identity/employment/education/certification are owned by employee
-- 
-- Dependencies: None (runs after 001_master_data)

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

-- Index for employee lookup by tenant
CREATE INDEX idx_employee_tenant ON employee(tenant_id);