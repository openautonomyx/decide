-- Traceability Migration
-- Add tables for internal traceability

-- Trace Session
CREATE TABLE trace_session (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenant(id),
    trace_id VARCHAR(64) NOT NULL,
    session_type VARCHAR(50),
    status VARCHAR(20),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    duration_ms FLOAT,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_trace_session_trace_id ON trace_session(trace_id);
CREATE INDEX ix_trace_session_tenant_id ON trace_session(tenant_id);

-- Trace Span Record
CREATE TABLE trace_span_record (
    id VARCHAR(36) PRIMARY KEY,
    trace_session_id VARCHAR(36) NOT NULL REFERENCES trace_session(id),
    span_id VARCHAR(64) NOT NULL,
    parent_span_id VARCHAR(64),
    service_name VARCHAR(255),
    operation_name VARCHAR(255),
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    duration_ms FLOAT,
    status_code VARCHAR(20),
    status_message TEXT,
    attributes TEXT,
    logs TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_trace_span_record_span_id ON trace_span_record(span_id);
CREATE INDEX ix_trace_span_record_session_id ON trace_span_record(trace_session_id);

-- Trace Link
CREATE TABLE trace_link (
    id VARCHAR(36) PRIMARY KEY,
    from_trace_session_id VARCHAR(36) NOT NULL REFERENCES trace_session(id),
    to_trace_session_id VARCHAR(36) REFERENCES trace_session(id),
    to_span_id VARCHAR(36),
    link_type VARCHAR(50),
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Usage Record
CREATE TABLE usage_record (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenant(id),
    trace_session_id VARCHAR(36) REFERENCES trace_session(id),
    metric_name VARCHAR(100) NOT NULL,
    quantity FLOAT DEFAULT 0.0,
    unit VARCHAR(20),
    cost FLOAT,
    period_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    period_end TIMESTAMP,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_usage_record_tenant_id ON usage_record(tenant_id);
CREATE INDEX ix_usage_record_metric_name ON usage_record(metric_name);