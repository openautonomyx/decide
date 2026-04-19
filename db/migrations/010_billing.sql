-- Billing Migration
-- Add tables for normalized billing events

-- Billing Adapter Binding
CREATE TABLE billing_adapter_binding (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenant(id),
    adapter_name VARCHAR(100) NOT NULL,
    adapter_type VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    config TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_billing_adapter_binding_tenant_id ON billing_adapter_binding(tenant_id);

-- Billing Account Binding
CREATE TABLE billing_account_binding (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenant(id),
    adapter_binding_id VARCHAR(36) REFERENCES billing_adapter_binding(id),
    external_account_id VARCHAR(100),
    account_name VARCHAR(255),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_billing_account_binding_tenant_id ON billing_account_binding(tenant_id);

-- Billing Event
CREATE TABLE billing_event (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenant(id),
    account_binding_id VARCHAR(36) REFERENCES billing_account_binding(id),
    event_type VARCHAR(50),
    event_name VARCHAR(100),
    quantity FLOAT DEFAULT 0.0,
    unit_price FLOAT,
    amount FLOAT,
    currency VARCHAR(3) DEFAULT 'USD',
    period_start TIMESTAMP,
    period_end TIMESTAMP,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_billing_event_tenant_id ON billing_event(tenant_id);
CREATE INDEX ix_billing_event_account_binding_id ON billing_event(account_binding_id);

-- Meter Definition
CREATE TABLE meter_definition (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenant(id),
    meter_name VARCHAR(100) NOT NULL,
    display_name VARCHAR(255),
    description TEXT,
    unit VARCHAR(20),
    unit_price FLOAT,
    aggregation_type VARCHAR(20) DEFAULT 'sum',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_meter_definition_tenant_id ON meter_definition(tenant_id);
CREATE INDEX ix_meter_definition_meter_name ON meter_definition(meter_name);